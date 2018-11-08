import serial
import io
import time
import picamera
import threading
from PIL import Image

s = serial.Serial("/dev/ttyACM0", 115200)
img = None
left_motor = 0
right_motor = 0

red = (255,0,0)
white = (255,255,255)
yellow = (255,255,0)

def isColor(color, pixl, diff=250):
	total_diff = abs(pixl[0]-color[0]) + abs(pixl[1]-color[1]) + abs(pixl[2]-color[2])
	if(total_diff < diff):
		return True
	else:
		return False

def isRed(pixl):
	return isColor(red, pixl)

def isWhite(pixl):
	return isColor(white, pixl)

def isYellow(pixl):
	return isColor(yellow, pixl)

def lineFollowWindow(x_max, y_max):
	height = int(y_max/5)

	x_start = 0 # Useful for Yellow Line Following
	x_end = x_max

	y_start = int(y_max*0.4)
	y_end = y_start + height

	return(x_start, x_end, y_start, y_end)

def avgInWindow(x_start, x_end, y_start, y_end, colorFunc):
	x_avg = 0
	y_avg = 0
	num_positive = 0

	for i in range(x_start, x_end):
		for j in range(y_start, y_end):
			global img
			if(colorFunc(img[i,j])):
				x_avg += i
				y_avg += j
				num_positive += 1

	if(not num_positive == 0):
		x_avg = int(x_avg/num_positive)
		y_avg = int(y_avg/num_positive)

	return (x_avg, y_avg, num_positive)

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
	num_pix = (x_max-x_min) * (y_max-y_min)
	return (percent/100) * num_pix

def fullProcess():
	#Do This
	global img

	right = (120,0)
	left = (0,120)
	straight = (120,120)

	x_max, y_max = img.size
	x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
	yellow_avg_x, yellow_y, yellow_pos = avgInWindow(x_start, x_end, y_start, y_end, isYellow)
	white_avg_x, white_y, white_pos = avgInWindow(x_start, x_end, y_start, y_end, isWhite)

	min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 5)

	if(yellow_pos > min_num_pixels and white_pos > min_num_pixels):
		if(white_avg_x < yellow_avg_x):
			print("Mid Err Right")
			return right
		#lane follow
		comp_yel = yellow_avg_x
		comp_white = x_max - white_avg_x
		if(abs(comp_yel - comp_white) < int(x_max/10)):
			print("Mid-S")
			return straight
		elif(comp_yel > comp_white):
			print("Mid-R")
			return right
		elif(comp_yel < comp_white):
			print("Mid-L")
			return left
		else:
			print("og idk")
			return (0,0)

	elif(yellow_pos > min_num_pixels and white_pos <= min_num_pixels):
		#Turn Right
		print("Right")
		return right
	elif(yellow_pos <= min_num_pixels and white_pos > min_num_pixels):
		#Turn Left
		print("Left")
		return left
	else:
		#I dont know
		print("IDK")
		return(0,0)


def send_to_arduino(s, cmd):
	s.write((cmd + ".").encode('utf-8'))
	s.flush()

def activate_motors(serial, left, right):
	send_to_arduino(serial, "1 {0} {1}".format(left, right))


def run_image_updater():
	with picamera.PiCamera() as camera:
		camera.start_preview()
		time.sleep(2)
		while(True):
			global img
			stream = io.BytesIO()
			camera.capture(stream, format='jpeg')
			stream.seek(0)
			im = Image.open(stream)
			pix = im.load()
			img = pix

def run_image_recognition():
	while(img == None):
		global img
		print("zzz")
		time.sleep(0.5)
	while(True):
		print("In Loop")
		left_motor, right_motor = fullProcess()
		activate_motors(s, left_motor, right_motor)

#Main
t1 = threading.Thread(target=run_image_updater)
t2 = threading.Thread(target=run_image_recognition)

t1.start()
t2.start()

t1.join()
t2.join()

activate_motors(s, 0, 0)