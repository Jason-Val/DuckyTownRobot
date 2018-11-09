import serial
import io
import time
import picamera
import threading
from PIL import Image

s = serial.Serial("/dev/ttyACM0", 115200)
img = None
x_max = 0
y_max = 0

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
	return isColor(white, pixl, 100)

def isYellow(pixl):
	return isColor(yellow, pixl, 200)

def lineFollowWindow(x_max, y_max):
	height = int(y_max/7)

	x_start = 0 # Useful for Yellow Line Following
	x_end = x_max

	y_start = int(y_max*0.5)
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
	global x_max
	global y_max

	hard_right = (125,0)
	right = (145,110)
	soft_right = (140,125)
	straight = (130,130)
	soft_left = (125,140)
	left = (110,145)
	hard_left = (0,125)

	x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
	yellow_avg_x, yellow_y, yellow_pos = avgInWindow(x_start, x_end, y_start, y_end, isYellow)
	white_avg_x, white_y, white_pos = avgInWindow(x_start, x_end, y_start, y_end, isWhite)

	min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 1)

	if(yellow_pos > min_num_pixels and white_pos > min_num_pixels):
		#We see both the yellow and white line
		#This is the case we want
		avg = (white_avg_x + yellow_avg_x)/2
		mid = x_max/2
		incr = x_max/100

		if(avg < incr*40):
			print("Left Both")
			return left
		elif(avg < incr*45):
			print("Soft Left Both")
			return soft_left
		elif(avg < incr*55):
			print("Straight Both")
			return straight
		elif(avg < incr*65):
			print("Soft Right Both")
			return soft_right
		elif(avg < incr*100):
			print("Right Both")
			return right
		else:
			print("This case should never happen")
			return (0,0)

	elif(yellow_pos > min_num_pixels and white_pos <= min_num_pixels):
		#Turn Right
		print("Right Yellow Only")
		# return hard_right
		return right
	elif(yellow_pos <= min_num_pixels and white_pos > min_num_pixels):
		#Turn Left
		print("Left White Only")
		# return hard_left
		return left
	else:
		print("No Yellow Or White")
		#Search
		return(0,0)
	return (0,0)


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
			global x_max
			global y_max
			x_max, y_max = im.size
			pix = im.load()
			img = pix

def run_image_recognition():
	while(img == None):
		global img
		# print("zzz")
		time.sleep(0.5)
	while(True):
		# print("In Loop")
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