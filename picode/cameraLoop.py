 
from picamera import PiCamera
from time import sleep

camera1 = PiCamera()
camera1.start_preview()
sleep(3)

i = 0

while (True):
    input()
    print("Taking Pic Number " + str(i))
    name = '/home/pi/Desktop/StopLights/img'
    name += str(i)
    name += '.jpg'
    camera1.capture(name)
    i+=1

camera1.stop_preview()
