#!/usr/bin/env python
import numpy as np
import cv2
from subprocess import call
import sys
import re
from datetime import date, datetime, timedelta
import collections
import math
import socket
import time
from PIL import Image as im 
import threading
import os
import serial 

# Change these parameters to the right addresses/ports for the servers
HOST = "192.168.1.11"   
THERMAL_PORT = 65432 
LIDAR_PORT = 65431
esp32_URL = "http://192.168.1.14"

#various parameters related to connecting to sensors, threading, and recording
esp32_cap = None 			
thermalCapture = None 			
arduino =  None 
thermalLock = threading.Lock()
lidarLock = threading.Lock()
distance = -1
arduinoConnected = False
showThermalFeed = False
showLidar = False 
showVideoFeed = False
recording = False
readyToConnectToLidar = False
readyToConnectToThermal = False
lidarFile = None
thermalVideoWriter = None
rgbVideoWriter = None


#GUI parameters: sizes and positions of components
nameOfWindow = "Blimp Controller Screen"
windowWidth = 1270
windowHeight = 480
thermalImageWidth = 320
thermalImageHeight = 240
rgbImageWidth = thermalImageWidth
rgbImageHeight = thermalImageHeight
resized_thermal_image = np.zeros((thermalImageHeight, thermalImageWidth, 3), dtype=np.uint8) 
panelStartPoint= (150, 150)
sizeFactor = (133.3, 100.0)
my_image = np.zeros((windowHeight, windowWidth, 3), dtype=np.uint8) #this is our main frame where we draw everything
boxLength = (133.3, 133.0)

fwd_pt1 = (int((0 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1]))
fwd_pt2 = (int((1 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1]))
fwd_pt3 = (int((0.5 * sizeFactor[0]) + panelStartPoint[0]), int(-((math.sqrt(5)/2.0) * sizeFactor[1]) + panelStartPoint[1]))

back_pt1 = (int((0 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1] + boxLength[1]))
back_pt2 = (int((1 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1] + boxLength[1]))
back_pt3 = (int((0.5 * sizeFactor[0]) + panelStartPoint[0]), int(((math.sqrt(5)/2.0) * sizeFactor[1]) + panelStartPoint[1] + boxLength[1]))

left_pt1 = (int((0 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1]))
left_pt2 = (int((0 * sizeFactor[0]) + panelStartPoint[0]), int((0 * sizeFactor[1]) + panelStartPoint[1] + boxLength[1]))
left_pt3 = (int(-((math.sqrt(5)/2.0) * sizeFactor[1]) + panelStartPoint[0]), int((0.5 * sizeFactor[0]) + panelStartPoint[1]))

right_pt1 = (int((0 * sizeFactor[0]) + panelStartPoint[0] + boxLength[0]), int((0 * sizeFactor[1]) + panelStartPoint[1]))
right_pt2 = (int((0 * sizeFactor[0]) + panelStartPoint[0] + boxLength[0]), int((0 * sizeFactor[1]) + panelStartPoint[1] + boxLength[1]))
right_pt3 = (int(((math.sqrt(5)/2.0) * sizeFactor[1]) + panelStartPoint[0]  + boxLength[0]), int((0.5 * sizeFactor[0]) + panelStartPoint[1]))

up_button_start = (panelStartPoint[0]-140, panelStartPoint[1]+260)
up_button_end = (panelStartPoint[0]+60, panelStartPoint[1]+310)
down_button_start = (panelStartPoint[0]+70, panelStartPoint[1]+260)
down_button_end = (panelStartPoint[0]+270, panelStartPoint[1]+310)
connectThermal_button_start = (panelStartPoint[0]+300, panelStartPoint[1]+260)
connectThermal_button_end = (panelStartPoint[0]+495, panelStartPoint[1]+310)
connectLidar_button_start = (panelStartPoint[0]+505, panelStartPoint[1]+260)
connectLidar_button_end = (panelStartPoint[0]+700, panelStartPoint[1]+310)
connectArduino_button_start = (panelStartPoint[0]+710, panelStartPoint[1]+260)
connectArduino_button_end = (panelStartPoint[0]+905, panelStartPoint[1]+310)
connectEsp32_button_start = (panelStartPoint[0]+915, panelStartPoint[1]+260)
connectEsp32_button_end = (panelStartPoint[0]+1110, panelStartPoint[1]+310)
record_button_start = (panelStartPoint[0]+300, panelStartPoint[1]+200)
record_button_end  = (panelStartPoint[0]+495, panelStartPoint[1]+250)
lidar_field_start = (panelStartPoint[0]+710, panelStartPoint[1]+200)
lidar_field_end = (panelStartPoint[0]+910, panelStartPoint[1]+250)
thermalImageStart = (connectThermal_button_start[0]+10, 20)
thermalImageEnd = (thermalImageStart[0]+thermalImageWidth, thermalImageStart[1]+thermalImageHeight)#80, 60
rgbVideoStart = (connectThermal_button_start[0]+335, 20)
rgbVideoEnd = (rgbVideoStart[0]+thermalImageWidth, rgbVideoStart[1]+thermalImageHeight)


#Functions
#This function sets up a thread to gather thermal data
def task1Thermal():

	global readyToConnectToThermal, resized_thermal_image
	t = threading.currentThread()
	print("Task 1 Thermal assigned to thread: {}".format(threading.current_thread().name))
	thermal_chunks = ""
	index = -1

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, THERMAL_PORT))
			print("Connected to thermal host")
			while (getattr(t, "do_run", True)): #this loops getting thermal images
				stamp = time.monotonic()
				while (getattr(t, "do_run", True) and showThermalFeed): #this loops asking for data until we get a full frame
					s.sendall(b"0") #ask server for data
					new_chunk = s.recv(4096)
					if new_chunk == b"":
						print("Problem: received no thermal data.  Try again later")
						time.sleep(0.5)
						break
					print("Received data from thermal server")

					thermal_chunks += new_chunk.decode()
					index = thermal_chunks.find("\n") #end of frame marker
					#print(index)
					if (index != -1):
						print("Received a complete thermal data frame")
						break

				string_data = thermal_chunks[:index]
				int_list_data = [x.strip() for x in (string_data[1:-1]).split(',')] #The 1: -1 is to remove the square brackets []
				thermal_chunks = thermal_chunks[index+1:] #remove our new frame from the buffer, also removing \n
				arr = np.array(int_list_data, dtype=np.uint8)
				array_reshaped = np.reshape(arr, (24, 32))
				rotated_image = cv2.rotate(array_reshaped, cv2.ROTATE_90_COUNTERCLOCKWISE)
				resized1 = cv2.resize(rotated_image, (thermalImageWidth, thermalImageHeight))

				#here we access an outside variable we can show
				with thermalLock:
					print("Received thermal lock in thermal thread")
					resized_thermal_image = cv2.cvtColor(resized1,cv2.COLOR_GRAY2RGB)			
				
				print("Time to get and set up one frame: %0.2f s" % (time.monotonic() - stamp))
	except Exception as e:
		print(f"Exception: {e}")
		while getattr(t, "do_run", True):
			time.sleep(1)

	finally:

		print("Stopping thermal thread!")

#This function sets up a thread to gather lidar data
def task2Lidar():

	global distance
	t = threading.currentThread()
	print("Task 2 Lidar assigned to thread: {}".format(threading.current_thread().name))
	lidar_chunks = ""

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST, LIDAR_PORT))
		print("Connected to lidar host")
		while (getattr(t, "do_run", True)): #this loops getting distances
			stamp = time.monotonic()
			time.sleep(0.01)
			while (getattr(t, "do_run", True) and showLidar): #this loops asking for data until we get a full distance
				s.sendall(b"1") #ask server for lidar data
				time.sleep(0.01)
				new_chunk = s.recv(1024) 
				if new_chunk == b"":
					print("Problem: received no lidar data. Try again later.")
					time.sleep(0.5)
					break
				print("Received data from the lidar server")

				lidar_chunks += new_chunk.decode()
				index = lidar_chunks.find("\n") #end of frame marker
	
				#print("index", index)
				if (index != -1):
					print("Received a complete lidar data frame")
					break

			string_data=lidar_chunks[:index]

			#here we need to again access an outside variable
			with lidarLock:
				distance = int(string_data)
			#as an example, we are getting one lidar distance here
			#we can also just use strings for any number of lidar values
			#or cast them all to ints, etc.
			#e.g.: distance_string= string_data
			#or: distances_ints_list = map(int, string_data.strip().split(','))

			lidar_chunks= lidar_chunks[index+1:] #remove our new frame from the buffer, also removing \n
			time.sleep(0.01)		
			print("Time to get and show one value: %0.2f s" % (time.monotonic() - stamp))

		s.close()

	except Exception as e:
		print(f"Exception: {e}")
		while getattr(t, "do_run", True):
			time.sleep(1)

	finally:
		print("Stopping lidar thread!")


#This helper function checks if a triangular button is pressed
#from https://www.w3resource.com/python-exercises/basic/python-basic-1-exercise-40.php
def pointIsInsideTriangle(x1, y1, x2, y2, x3, y3, xp, yp):

	# Calculate the cross products (c1, c2, c3) for the point relative to each edge of the triangle
	c1 = (x2 - x1) * (yp - y1) - (y2 - y1) * (xp - x1)
	c2 = (x3 - x2) * (yp - y2) - (y3 - y2) * (xp - x2)
	c3 = (x1 - x3) * (yp - y3) - (y1 - y3) * (xp - x3)

	# Check if all cross products have the same sign (inside the triangle) or different signs (outside the triangle)
	if (c1 < 0 and c2 < 0 and c3 < 0) or (c1 > 0 and c2 > 0 and c3 > 0):
		return True
	return False

#This helper function just checks if the user has pressed a rectangular button
#from https://www.geeksforgeeks.org/check-if-a-point-lies-on-or-inside-a-rectangle-set-2/
def pointIsInsideRectangle(x1, y1, x2, y2, x, y):
    if (x > x1 and x < x2 and y > y1 and y < y2):
        return True
    else:
        return False

#This helper function just sends a message to the blimp controller and prints the response
def sendMessageToArduino(message):
	if(arduinoConnected == True):
		arduino.write(bytes(message, 'utf-8')) 
		time.sleep(0.05) 
		data = arduino.readline()
		data2=(data.decode("utf-8")).strip() 
		print(data2)

#Mouse callback function
def process_mouse_event(event, x, y, flags, param): 
	global showThermalFeed, showLidar, recording, arduinoConnected, lidarFile, thermalVideoWriter, arduino, showVideoFeed, rgbVideoWriter, thermalCapture, esp32_cap, readyToConnectToThermal, t1, t2 

	if event == cv2.EVENT_LBUTTONDOWN: 
		print("Mouse clicked:", x, y)
		if(pointIsInsideTriangle(fwd_pt1[0], fwd_pt1[1], fwd_pt2[0], fwd_pt2[1], fwd_pt3[0], fwd_pt3[1],x,y)):
			print("Forward")
			sendMessageToArduino("6") #this is okay because we check if we are connected to the Arduino within this function
		elif(pointIsInsideTriangle(back_pt1[0], back_pt1[1], back_pt2[0], back_pt2[1], back_pt3[0], back_pt3[1],x,y)):
			print("Backward")
			sendMessageToArduino("7")
		elif(pointIsInsideTriangle(left_pt1[0], left_pt1[1], left_pt2[0], left_pt2[1], left_pt3[0], left_pt3[1],x,y)):
			print("Left")
			sendMessageToArduino("8")
		elif(pointIsInsideTriangle(right_pt1[0], right_pt1[1], right_pt2[0], right_pt2[1], right_pt3[0], right_pt3[1],x,y)):
			print("Right")
			sendMessageToArduino("9")
		elif(pointIsInsideRectangle(up_button_start[0], up_button_start[1], up_button_end[0], up_button_end[1],x,y)):
			print("Up")
			sendMessageToArduino("0")
		elif(pointIsInsideRectangle(down_button_start[0], down_button_start[1], down_button_end[0], down_button_end[1],x,y)):
			print("Down")
			sendMessageToArduino("1")

		#arduino connect/disconnect
		elif(pointIsInsideRectangle(connectArduino_button_start[0], connectArduino_button_start[1], connectArduino_button_end[0], connectArduino_button_end[1],x,y)):			
			if(arduinoConnected == False):
				print("Connect to Arduino")
				#redraw rectangle and text
				cv2.rectangle(my_image, connectArduino_button_start, connectArduino_button_end, (255, 127, 127), thickness=-1)
				cv2.putText(my_image, "Disconnect Arduino", (connectArduino_button_start[0]+10, connectArduino_button_start[1]+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)				
				arduino =  serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
				arduinoConnected = True
			else:
				arduinoConnected = False
				arduino =  None 
				print("Disconnect from Arduino")
				cv2.rectangle(my_image, connectArduino_button_start, connectArduino_button_end, (255, 0, 0), thickness=-1)
				cv2.putText(my_image, "Connect Arduino", (connectArduino_button_start[0]+10, connectArduino_button_start[1]+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)

		#thermal connect/disconnect
		elif(pointIsInsideRectangle(connectThermal_button_start[0], connectThermal_button_start[1], connectThermal_button_end[0], connectThermal_button_end[1],x,y)):			
			if(showThermalFeed == False):
				print("Connect to Thermal Camera and Show Feed")
				readyToConnectToThermal= True
				t1 = threading.Thread(target=task1Thermal, name='t1')
				t1.start()
				t1.do_run = True

				cv2.rectangle(my_image, connectThermal_button_start, connectThermal_button_end, (255, 127, 127), thickness=-1)
				cv2.putText(my_image, "Disconnect Therm.", (connectThermal_button_start[0]+5, connectThermal_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
				showThermalFeed = True
			else:
				showThermalFeed = False
				t1.do_run = False
				t1.join()
				print("Disconnect from Thermal Camera and Hide Feed")
				cv2.rectangle(my_image, connectThermal_button_start, connectThermal_button_end, (255, 0, 0), thickness=-1)
				cv2.rectangle(my_image, thermalImageStart, thermalImageEnd, (0, 0, 0), thickness=-1)
				cv2.putText(my_image, "Connect Thermal", (connectThermal_button_start[0]+10, connectThermal_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)

		#esp32cam connect/disconnect
		elif(pointIsInsideRectangle(connectEsp32_button_start[0], connectEsp32_button_start[1], connectEsp32_button_end[0], connectEsp32_button_end[1],x,y)):			
			if(showVideoFeed == False):
				print("Connect to ESP32 and Show Video Feed")
				esp32_cap = cv2.VideoCapture(esp32_URL + ":81/stream")
				cv2.rectangle(my_image, connectEsp32_button_start, connectEsp32_button_end, (255, 127, 127), thickness=-1)
				cv2.putText(my_image, "Disconnect Video", (connectEsp32_button_start[0]+5, connectEsp32_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
				showVideoFeed = True
			else:
				showVideoFeed = False
				print("Disconnect from ESP32 and Hide Feed")
				cv2.rectangle(my_image, connectEsp32_button_start, connectEsp32_button_end, (255, 0, 0), thickness=-1)
				cv2.rectangle(my_image, rgbVideoStart, rgbVideoEnd, (0, 0, 0), thickness=-1)
				cv2.putText(my_image, "Connect Video", (connectEsp32_button_start[0]+10, connectEsp32_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1) 
				esp32_cap.release()

		#lidar connect/disconnect
		elif(pointIsInsideRectangle(connectLidar_button_start[0], connectLidar_button_start[1], connectLidar_button_end[0], connectLidar_button_end[1],x,y)):
			if(showLidar == False):
				print("Connect to Lidar and Show")
				t2 = threading.Thread(target=task2Lidar, name='t2')
				t2.start()
				t2.do_run = True
				readyToConnectToLidar= True #let the thread try to connect to the server
				cv2.rectangle(my_image, connectLidar_button_start, connectLidar_button_end, (255, 127, 127), thickness=-1)
				cv2.putText(my_image, "Disconnect Lidar", (connectLidar_button_start[0]+10, connectLidar_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
				showLidar = True
			else:
				showLidar = False
				t2.do_run = False
				t2.join()
				print("Disconnect from Lidar and Hide")
				cv2.rectangle(my_image, connectLidar_button_start, connectLidar_button_end, (255, 0, 0), thickness=-1)
				cv2.putText(my_image, "Connect Lidar", (connectLidar_button_start[0]+10, connectLidar_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
				
		#record data
		elif(pointIsInsideRectangle(record_button_start[0], record_button_start[1], record_button_end[0], record_button_end[1] ,x,y)):
			#for simplicity, we need to be connected to all sensors
			if(recording == False and showThermalFeed and showLidar and showVideoFeed): 				
				print("Starting to Record")
				currentDateAndTime = time.strftime("%Y%m%d-%H%M%S")
				lidarFileName = "lidarData/blimp_lidar" + currentDateAndTime + ".txt" 
				thermalFileName = "thermalData/blimp_thermal_" + currentDateAndTime + ".avi"
				rgbFileName = "rgbData/blimp_rgb_" + currentDateAndTime + ".avi"
				lidarFile = open(lidarFileName,'a')
				thermalVideoWriter = cv2.VideoWriter(thermalFileName, cv2.VideoWriter_fourcc(*'MJPG'), 1, (thermalImageWidth, thermalImageHeight))
				rgbVideoWriter = cv2.VideoWriter(rgbFileName, cv2.VideoWriter_fourcc(*'MJPG'), 5, (rgbImageWidth, rgbImageHeight))
				cv2.rectangle(my_image, record_button_start, record_button_end, (127, 127, 255), thickness=-1)
				cv2.putText(my_image, "Stop Recording", (record_button_start[0]+10, record_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
				recording = True
			else:
				recording = False
				time.sleep(0.1) #hopefully this makes sure the files are no longer being used
				print("Stopping Recording")
				cv2.rectangle(my_image, record_button_start, record_button_end, (0, 0, 255), thickness=-1)
				cv2.putText(my_image, "Record", (record_button_start[0]+10, record_button_start[1]+35 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
				lidarFile.close()
				thermalVideoWriter.release() 
				rgbVideoWriter.release() 
	return None


t1 = threading.Thread(target=task1Thermal, name='t1')
t2 = threading.Thread(target=task2Lidar, name='t2')


def main():

	global distance, resized_thermal_image, t1, t2

	#set up the window
	cv2.namedWindow(nameOfWindow)
	cv2.moveWindow(nameOfWindow, 50,100)
	cv2.resizeWindow(nameOfWindow, windowWidth, windowHeight)
	cv2.setMouseCallback(nameOfWindow, process_mouse_event)

	#draw the GUI components
	triangle_cnt = np.array([fwd_pt1, fwd_pt2, fwd_pt3])
	cv2.drawContours(my_image, [triangle_cnt], 0, (0,255,0), -1)

	triangle_cnt = np.array([back_pt1, back_pt2, back_pt3])
	cv2.drawContours(my_image, [triangle_cnt], 0, (0,255,0), -1)

	triangle_cnt = np.array([left_pt1, left_pt2, left_pt3])
	cv2.drawContours(my_image, [triangle_cnt], 0, (0,255,0), -1)

	triangle_cnt = np.array([right_pt1, right_pt2, right_pt3])
	cv2.drawContours(my_image, [triangle_cnt], 0, (0,255,0), -1)

	cv2.rectangle(my_image, up_button_start, up_button_end, (0, 255, 0), thickness=-1)
	cv2.rectangle(my_image, down_button_start, down_button_end, (0, 255, 0), thickness=-1)
	cv2.rectangle(my_image, connectThermal_button_start, connectThermal_button_end, (255, 0, 0), thickness=-1)
	cv2.rectangle(my_image, connectLidar_button_start, connectLidar_button_end, (255, 0,0), thickness=-1)
	cv2.rectangle(my_image, connectArduino_button_start, connectArduino_button_end, (255, 0, 0), thickness=-1)
	cv2.rectangle(my_image, lidar_field_start, lidar_field_end, (255, 255, 255), thickness=-1)
	cv2.rectangle(my_image, record_button_start, record_button_end, (0, 0, 255), thickness=-1)
	cv2.rectangle(my_image, connectEsp32_button_start, connectEsp32_button_end, (255, 0,0), thickness=-1)

	#add some text labels
	cv2.putText(my_image, "Fwd", (fwd_pt1[0]+40, fwd_pt1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Back", (back_pt1[0]+30, back_pt1[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Left", (left_pt1[0]-70, left_pt1[1]+70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Right", (right_pt1[0]+10, right_pt1[1]+70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Up", (up_button_start[0]+75, up_button_start[1]+35 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Down", (down_button_start[0]+75, down_button_start[1]+35 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Connect Thermal", (connectThermal_button_start[0]+10, connectThermal_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
	cv2.putText(my_image, "Connect Lidar", (connectLidar_button_start[0]+10, connectLidar_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
	cv2.putText(my_image, "Connect Arduino", (connectArduino_button_start[0]+10, connectArduino_button_start[1]+35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)
	cv2.putText(my_image, "Record", (record_button_start[0]+10, record_button_start[1]+35 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
	cv2.putText(my_image, "Lidar", (lidar_field_start[0]-100, lidar_field_start[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
	cv2.putText(my_image, "Connect Video", (connectEsp32_button_start[0]+10, connectEsp32_button_start[1]+35 ), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (255, 255, 255), 1)

	cv2.imshow(nameOfWindow, my_image)
	counter=0

	while True:

		if(showLidar): 
			cv2.rectangle(my_image, lidar_field_start, lidar_field_end, (255, 255, 255), thickness=-1) #clear the lidar field
			with lidarLock:				
				cv2.putText(my_image, str(distance), (lidar_field_start[0]+10, lidar_field_start[1]+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 2)
				#if we are using 3 lidars e.g., replace "str(distance)"
				#with "distance_string"

		if(showThermalFeed):
			with thermalLock:
				my_image[thermalImageStart[1]:thermalImageEnd[1], thermalImageStart[0]:thermalImageEnd[0], :] = resized_thermal_image 

		if(showVideoFeed):
			print("got video lock in main")
			if esp32_cap.isOpened(): 
				ret, videoImage = esp32_cap.read()
				resized_videoImage = cv2.resize(videoImage, (rgbImageWidth, rgbImageHeight))
				my_image[rgbVideoStart[1]:rgbVideoEnd[1], rgbVideoStart[0]:rgbVideoEnd[0], :] = resized_videoImage

		#write data to files
		if(recording):
			if(showLidar):
				with lidarLock:
					currentDateAndTime = time.strftime("%Y%m%d-%H%M%S")
					lidarFile.write(currentDateAndTime + ": " + (str(distance) + "\n"))
			if(showThermalFeed):
				with thermalLock:
					thermalVideoWriter.write(resized_thermal_image)
			if(showVideoFeed):
				rgbVideoWriter.write(resized_videoImage)
		
		cv2.imshow(nameOfWindow, my_image)

		key= cv2.waitKey(10) & 0xFF 

		if(key== ord("q")): #quit 
			break

	#free up resources
	if(showThermalFeed):
		t1.do_run = False
		t1.join()
	if(showLidar):
		t2.do_run = False
		t2.join()
	if(showVideoFeed):
		esp32_cap.release()
	if(recording):
		if(showLidar):
			lidarFile.close()
		if(showThermalFeed):
			thermalVideoWriter.release()
		if(showVideoFeed):
			rgbVideoWriter.release()

	cv2.destroyAllWindows()
	print ("Closing program")

if __name__== '__main__':

	print('-------------------------------------')
	print('-        BLIMP CONTROLLER           -')
	print('-   APR 2025, HH, Martin Cooney     -')
	print('-------------------------------------')

	main()




