# Crime_Blimp
 Goodies to help you to detect evidence with a blimp


Blimp for Crime Scene Analysis

Basic Concept
Crime is a horrible problem, and important evidence is often destroyed.
We believe blimps can be used like floating cameras to drift over sensitive evidence and record it without destroying it (e.g., due to human contamination or wind).
(Details in an exploratory paper/video for SAIS 2025: https://youtu.be/5ep9UeChn68)
This rep contains a number of goodies that you could help you to try out our setup if you wanted.

Content (requirements, files)

Requirements: environment with Python 3 and OpenCV; a remoted RPI set up to read a thermal cameras (MLX90640) and 1-3 lidars (TF-Lunas); an Esp32cam with standard server code ("CameraWebServer") (see Google/their webpages for how to do that) 

Folders:
blimp_gui: this is a user interface to help you to control your blimp (or other similar robot--all in OpenCV so no other irritating dependencies)
bloodstains: this is rough code to let you detect and classify 3 kinds of bloodstains!: passive, active, and transfer
random_crime_scene_generators: this can create random crime scenes for testing
servers: these are some simple servers to put on your RPI

(Note: This code was written using the author's setup described above for exploratory research purposes; the author cannot help with getting it to work on the reader's system.)



