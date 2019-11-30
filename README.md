# Robotic_arm_Object_Detection 0.1.0.3

  This repository is the result of a summer internship at Rozum Robotics company. Our goal was to teach robotic arm to detect objects(cube) on work place and sort it by colors.
  
[![Alt text](https://www.youtube.com/watch?v=yIhqKh4P_Z4&feature=youtu.be)

# Equipment:

  - Robotic Arm Pulse 75
  - Web camera Logitech c270
  - Festo Vacuum gener
  - Camozzi Solenoid valve
  - Kids cubes 40x40x40 mm

# Soft:

  We tested our project on Ubuntu 16.04 and Windows 10
  - Ubuntu 16.04, 18.04 / Windows 10
  - OpenCV 4.10
  - PyQt 5
  - Sklearn
  - Keras

# Approach:

  First of all we tries to get result only with standard computer vision approaches like:

   1. Transforming image in HSV format in order to remove problems with changing lighting
   2. Selecting parameters H S V for removing background
   3. Using Canny Edge detection and Find contours functions
   4. Using color regions to define colors

  This approach only worked in static and isn't worked with changing lighting. That why we used Unet to define mask and then used watershed segmentation to detect object, even they stand quite close. It's given us robust system

# Camera intrinsic parameters

   Logitech C270 Webcam

   - Resolution: 1280x720
   - Pixel Size: 2.8um
   - Sensor Size: 3.58x2.02mm
   - Stock lens focal length: 4.2mm
