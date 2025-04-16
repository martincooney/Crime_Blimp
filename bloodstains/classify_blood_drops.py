#!/usr/bin/env python
import numpy as np
import cv2
import math

#from https://www.geeksforgeeks.org/check-if-a-point-lies-on-or-inside-a-rectangle-set-2/
def pointIsInsideRectangle(x1, y1, x2, y2, x, y):
    if (x > x1 and x < x2 and y > y1 and y < y2):
        return True
    else :
        return False

print('-----------------------------------------------')
print('-     DETECTING KINDS OF BLOOD PATTERNS       -')
print('-        APR 2025, HH, Martin Cooney          -')
print('-----------------------------------------------')
print("") 

nameOfWindow="img"
inputFileName= "evidence.JPG"       #change as needed
img = cv2.imread(inputFileName)
print("Processing: inputFileName", inputFileName)
height, width = img.shape[:2] 

#draw 3 squares to show the ground truth
class1_rect_start = (2965,1615) #these values were found manually, change as needed...
class1_rect_end = (3955,2855)
class2_rect_start = (2990,265)
class2_rect_end = (3875, 1555)
class3_rect_start = (270,275)
class3_rect_end = (1125,1500)
cv2.rectangle(img,class3_rect_start,class3_rect_end,(255,0,0),20)
cv2.rectangle(img,class2_rect_start,class2_rect_end,(0,255,0),20)
cv2.rectangle(img,class1_rect_start,class1_rect_end,(0,0,255),20)

#find red (blood)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(img_hsv, (150,80,80), (180,255,255)) #just purple red, avoiding dark
cropped = cv2.bitwise_and(img, img, mask=mask)

#(optional: check that something was detected, not really needed...)
ys, xs = np.where(mask > 0) 
if not (len(xs) > 0 and len(ys) > 0):
	print("No blood pixels found.")

#find contours
(cnts, *_) = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

numberOfCorrect = 0
totalNumberOfReasonablySizedContours = 0
numberOutsideOfGroundTruth = 0

for c in cnts:	
	area = cv2.contourArea(c)
	if (area > 40.0): #check if the area is reasonable		
		totalNumberOfReasonablySizedContours+=1

		#(optional, show where the center of each contour is, not really needed)
		M = cv2.moments(c)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		cv2.circle(img, (cX, cY), 7, (255, 255, 255), -1)

		ellipse = cv2.fitEllipse(c)
		eccentricity= (ellipse[1][1]/ellipse[1][0])
		#cv2.ellipse(img, ellipse, (0,0,255), 3) #uncomment this to show ellipses
		#print("eccentricity", eccentricity) #this can also be uncommented 

		#find the groundtruth class label for this contour
		#we know that we have one paper sheet for each kind of bloodstain
		#so the region tells us what the bloodstain is
		groundtruthClass=-1
		if(pointIsInsideRectangle(class1_rect_start[0], class1_rect_start[1], class1_rect_end[0], class1_rect_end[1],cX,cY)):
			groundtruthClass=1
		elif(pointIsInsideRectangle(class2_rect_start[0], class2_rect_start[1], class2_rect_end[0], class2_rect_end[1],cX,cY)):
			groundtruthClass=2
		elif(pointIsInsideRectangle(class3_rect_start[0], class3_rect_start[1], class3_rect_end[0], class3_rect_end[1],cX,cY)):
			groundtruthClass=3
		else:
			numberOutsideOfGroundTruth+=1

		#now use simple heuristics to guess the type of bloodstain
		predictedClass=-1
		if (area > 5000.0): 				#guess transfer stain
			cv2.drawContours(img, [c], -1, (255, 0, 0), 10)
			predictedClass=3
		elif (eccentricity < 2 and eccentricity > 1.2): #guess active
			cv2.drawContours(img, [c], -1, (0, 255, 0), 10)
			predictedClass=2
		else: 						#guess passive
			cv2.drawContours(img, [c], -1, (0, 0, 255), 10)
			predictedClass=1

		if(groundtruthClass==predictedClass):
			numberOfCorrect+=1

if(totalNumberOfReasonablySizedContours>0):
	accuracy= (numberOfCorrect/totalNumberOfReasonablySizedContours)
	print("Overall Accuracy:", (accuracy*100), "%")
	print("Number of Correct Samples:", numberOfCorrect)
	print("Total Number of Reasonably Sized Contours:", totalNumberOfReasonablySizedContours)
	accuracyOfBloodOnly= (numberOfCorrect/(totalNumberOfReasonablySizedContours- numberOutsideOfGroundTruth))
	print("Accuracy Of Blood Only:", (accuracyOfBloodOnly*100), "%")
	print("Number of Blood Contours:", (totalNumberOfReasonablySizedContours- numberOutsideOfGroundTruth))
	print("Number of Non-blood Contours:", numberOutsideOfGroundTruth)
else:
	print("No contours detected.")

#optional: our input image is large, so let's make it smaller to make it easy to see
img_small = cv2.resize(img, (int(0.2*width), int(0.2*height)), interpolation = cv2.INTER_CUBIC)

#show the result and finally save it
cv2.namedWindow(nameOfWindow)
cv2.imshow(nameOfWindow, img_small)
cv2.waitKey()
cv2.imwrite("blood_pattern_kind_detected.png", img_small)
cv2.destroyAllWindows()


