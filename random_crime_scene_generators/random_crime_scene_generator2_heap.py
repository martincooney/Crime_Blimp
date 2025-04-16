import cv2 
import numpy as np
import random
from itertools import permutations 
from datetime import date, datetime, timedelta
import time

#here the user should tweak these parameters as desired
width=640
height=480
counter= 1
other_evidence=["knife 1", "knife 2", "shoes", "blood 1", "blood 2", "blood 3"]
number_of_trials = 20


for i in range(number_of_trials):

	#make a blank white image
	image = np.zeros((height,width,3), np.uint8)
	image[:,:,0]=255
	image[:,:,1]=255
	image[:,:,2]=255

	#draw a 2 by 4 grid with 3 vertical lines and 1 horizontal line
	horizontal_line_y= int(height/2)
	vertical_line1_x = int(width/4)
	vertical_line2_x = int(width/2)
	vertical_line3_x = int((width*3)/4)
	cv2.line(image, (0, horizontal_line_y), (width, horizontal_line_y), (125, 125, 125))
	cv2.line(image, (vertical_line1_x, 0), (vertical_line1_x, height), (125, 125, 125))
	cv2.line(image, (vertical_line2_x, 0), (vertical_line2_x, height), (125, 125, 125))
	cv2.line(image, (vertical_line3_x, 0), (vertical_line3_x, height), (125, 125, 125))

	#first, we decide the location of big objects, then fill in the rest
	#for simplicity, in this example, we only have one big object, a gun
	#and we say it can only be in 4 places in the 8 cell grid (no rotations)
	evidenceByPosition=["", "", "", "", "", "", "", ""]
	firearm_position= random.randint(0, 3)
	if (firearm_position==0):
		evidenceByPosition[0]= "firearm"
		evidenceByPosition[1]= "firearm"
	elif (firearm_position==1):
		evidenceByPosition[2]= "firearm"
		evidenceByPosition[3]= "firearm"	
	elif (firearm_position==2):
		evidenceByPosition[4]= "firearm"
		evidenceByPosition[5]= "firearm"
	else:
		evidenceByPosition[6]= "firearm"
		evidenceByPosition[7]= "firearm"

	#now fill in the small 1 cell samples
	for e in other_evidence:
		found=False
		while(not found):
			r= random.randint(0, 7)
			if (evidenceByPosition[r]==""):
				evidenceByPosition[r]=e
				found=True
	print(evidenceByPosition)

	#add text to the image to show where the evidence is	
	cv2.putText(image, evidenceByPosition[0],(20,horizontal_line_y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[1],(vertical_line1_x+ 20,horizontal_line_y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[2],(vertical_line2_x+ 20,horizontal_line_y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[3],(vertical_line3_x+ 20,horizontal_line_y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[4],(20,height-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[5],(vertical_line1_x+ 20,height-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[6],(vertical_line2_x+ 20,height-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
	cv2.putText(image, evidenceByPosition[7],(vertical_line3_x+ 20,height-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

	#uncomment these lines to see the random images as they are created
	#cv2.imshow('image window', image)
	#cv2.waitKey(0)

	currentDateAndTime = time.strftime("%Y%m%d-%H%M%S")
	fileName= "experimentEvidenceLocations/evidenceLocations_" + str(counter) + "_" + currentDateAndTime + ".png" 
	cv2.imwrite(fileName, image)

	counter+=1

cv2.destroyAllWindows() #only needed if the user is viewing the images (see above)

