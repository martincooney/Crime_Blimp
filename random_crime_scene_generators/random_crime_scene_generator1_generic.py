import cv2 
import numpy as np
import random
from itertools import permutations 
from datetime import date, datetime, timedelta
import time


#here crimes and weapons can be added; e.g., "brass knuckles", "belt"
crimes = ["homicide", "assault", "burglary", "arson"]
weapons=["firearm", "knife", "pepper spray", "stun gun", "club/hammer", "makeshift weapon"] 


#here the user should select various parameters
kind_of_crime = "homicide"
floor_plan_image = "hint" #'NFC_villa' #choose a background image here
buffer= 20 #this specifies the minimal distance from the end of the image for text


#the user can tweak or make there own probabilities here
#PROBABILITIES
#homicide: 0.8 chance corpse, 0.8 chance weapon, 1-3 blood samples
#assault: 0.8 chance weapon, 1-3 blood samples
#burglary: 1-5 missing items, 1-5 destroyed items
#arson:  0.1 chance corpse, 0.8 chance fuel_source, 0.5 ignition_source #accelerant

homicide_params = {
  "corpse": 0.8,
  "weapon": 0.8,
  "blood": 3.0,
  "missing_item": 0.0,
  "vandalized_item": 0.0,
  "fuel_source": 0.0,
  "ignition_source": 0.0
}
assault_params = {
  "corpse": 0.0,
  "weapon": 0.8,
  "blood": 3.0,
  "missing_item": 0.0,
  "vandalized_item": 0.0,
  "fuel_source": 0.0,
  "ignition_source": 0.0
}
burglary_params = {
  "corpse": 0.0,
  "weapon": 0.0,
  "blood": 0.0,
  "missing_item": 5,
  "vandalized_item": 5,
  "fuel_source": 0.0,
  "ignition_source": 0.0
}
arson_params = {
  "corpse": 0.1,
  "weapon": 0.0,
  "blood": 0.0,
  "missing_item": 0.0,
  "vandalized_item": 0.0,
  "fuel_source": 0.8,
  "ignition_source": 0.5
}
 

if kind_of_crime == "homicide":
	crime_params= homicide_params
elif kind_of_crime == "assault":
	crime_params= assault_params
elif kind_of_crime == "burglary":
	crime_params= burglary_params
elif kind_of_crime == "arson":
	crime_params= arson_params


#load image
img = cv2.imread(floor_plan_image + '.png')
height = img.shape[0]
width = img.shape[1]


#below, for each kind of evidence, we calculate where it appears, etc.

#corpses, weapons, and blood are mostly for homicides and assault cases
r=random.random()
if r < crime_params["corpse"]:
	print("corpse found", r, crime_params["corpse"])

	#choose location
	corpse_x = random.randint(0, width-buffer)
	corpse_y = random.randint(0, height-buffer)

	#corpse in green
	cv2.putText(img, "corpse", (corpse_x, corpse_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 255, 0), 1)

r=random.random()
if r < crime_params["weapon"]:
	print("weapon found", r, crime_params["weapon"])

	#choose random weapon (only 1)
	weapon = "+" + random.choice(weapons)

	#choose location
	weapon_x = random.randint(0, width-buffer)
	weapon_y = random.randint(0, height-buffer)

	#weapons in blue
	cv2.putText(img, weapon, (weapon_x, weapon_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255, 0, 0), 1)

r= random.randint(0, crime_params["blood"]) #1-3
if r > 0:
	print("blood found", r, crime_params["blood"])
#for each blood sample
for i in range(r): 

	#choose location
	blood_x = random.randint(0, width-buffer)
	blood_y = random.randint(0, height-buffer)

	#choose kind of blood
	blood_pattern=""
	r= random.randint(0, 2)
	if r==0:
		blood_pattern="blood (passive)"
	elif r==1:
		blood_pattern="blood (active)"
	else:
		blood_pattern="blood (transfer)"

	#blood in red
	cv2.putText(img, blood_pattern, (blood_x, blood_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,0, 255), 1)


#for burglaries, we imagine missing and vandalized items
r= random.randint(0, crime_params["missing_item"]) #1-5
if r > 0:
	print("missing_item found", r, crime_params["missing_item"])
for i in range(r): 

	#choose location
	missing_item_x = random.randint(0, width-buffer)
	missing_item_y = random.randint(0, height-buffer)

	cv2.putText(img, "missing_item", (missing_item_x, missing_item_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (200, 30, 30), 1)

r= random.randint(0, crime_params["vandalized_item"]) #1-5
if r > 0:
	print("vandalized_item found", r, crime_params["vandalized_item"])
for i in range(r): 

	#choose location
	vandalized_item_x = random.randint(0, width-buffer)
	vandalized_item_y = random.randint(0, height-buffer)

	cv2.putText(img, "vandalized_item", (vandalized_item_x, vandalized_item_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 150, 50), 1)


#for arsons, fuel and ignitors might be found
r=random.random()
if r < crime_params["fuel_source"]:
	print("fuel_source found", r, crime_params["fuel_source"])

	#choose location
	fuel_source_x = random.randint(0, width-buffer)
	fuel_source_y = random.randint(0, height-buffer)

	cv2.putText(img, "fuel_source", (fuel_source_x, fuel_source_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (255, 255, 0), 1)

r=random.random()
if r < crime_params["ignition_source"]:
	print("ignition_source found", r, crime_params["ignition_source"])

	#choose location
	ignition_source_x = random.randint(0, width-buffer)
	ignition_source_y = random.randint(0, height-buffer)

	cv2.putText(img, "ignition_source", (fignition_source_x, ignition_source_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0, 255, 255), 1)

#show the resulting random crime scene and save it to file!
cv2.imshow('Random Crime Scene Generator', img)
cv2.waitKey(0)

currentDateAndTime = time.strftime("%Y%m%d-%H%M%S")
fileName= "randomCrimeScenes/randomCrimeScene_" + kind_of_crime + "_" + floor_plan_image + "_" + currentDateAndTime + ".png" 
cv2.imwrite(fileName, img)

cv2.destroyAllWindows()

