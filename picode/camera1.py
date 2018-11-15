 
from picamera import PiCamera
from time import sleep

camera1 = PiCamera()

camera1.start_preview()
sleep(3)
camera1.capture('/home/pi/Desktop/currImg.jpg')
camera1.stop_preview()
