#lidar code adapted from waveshare, server code adapted from various sources on google

import smbus
import time
import socket

#change these parameters as needed
HOST="192.168.1.211" 
PORT=65431 #different from thermal
bus = smbus.SMBus(1) 
address = 0x0A #lidar's I2C address, 10 in decimal (default address 0x10)

getLidarDataCmd = [0x5A,0x05,0x00,0x01,0x60] #Magic code to get lidar data
distance=0

def getLidarData(addr, cmd):
	bus.write_i2c_block_data(addr, 0x00, cmd)
	time.sleep(0.01)
	data = bus.read_i2c_block_data(addr, 0x00, 9)
	distance = data[0] | (data[1] << 8)
	return distance

try:
	distance= getLidarData(address, getLidarDataCmd)
	time.sleep(0.1)
except ValueError:
	print("Error: can't read lidar sensor")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen(10)
	while True: #loop for connections (clients can reconnect)
		print("Lidar Server: waiting for connection.")
		conn, addr = s.accept()
		with conn:
			print(f"Connected at {addr}")
			while True: #loop listening for messages
				data=conn.recv(1024)
				if not data:
					print("no data, break")
					break
				print(f"Received data {data}")

				if (data == b"1"):
					print("Received request for lidar data")

					stamp = time.monotonic()
					try:
						distance= getLidarData(address, getLidarDataCmd)
					except ValueError:
						print("Error: can't read lidar sensor")
						continue	
					time.sleep(0.1)
					print("distance:", distance)
					print("Time to read distance: %0.2f s" % (time.monotonic() - stamp))
					y = str(distance)
					y+="\n"
					y = y.encode()
					conn.sendall(y) 

