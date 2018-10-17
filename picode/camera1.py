Python 3.5.3 (default, Jan 19 2017, 14:11:04) 
[GCC 6.3.0 20170124] on linux
Type "copyright", "credits" or "license()" for more information.
>>> 
from picamera import PiCamera
from time import sleep

camera1 = PiCamera()

camera1.start_preview()
sleep(10)
camera1.stop_preview()
