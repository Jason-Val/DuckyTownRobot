import serial
import io
import time
import picamera
from PIL import Image

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

def avgInWindow(img, x_start, x_end, y_start, y_end, colorFunc):
	x_avg = 0
	y_avg = 0
	num_positive = 0

	for i in range(x_start, x_end):
		for j in range(y_start, y_end):
			if(colorFunc(img[i,j])):
				x_avg += i
				y_avg += j
				num_positive += 1

	if(not num_positive == 0):
		x_avg = int(x_avg/num_positive)
		y_avg = int(y_avg/num_positive)

	return (x_avg, y_avg, num_positive)

def lineFollowWindow(x_max, y_max):
	width = int(x_max - 1)
	height = int(y_max/15)

	# x_start = int(x_max*0.5) # Useful for While Line Following
	x_start = 0 # Useful for Yellow Line Following
	x_end = x_start + width

	y_start = int(y_max*0.6)
	y_end = y_start + height

	return(x_start, x_end, y_start, y_end)

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
	num_pix = (x_max-x_min) * (y_max-y_min)
	return (percent/100) * num_pix

def getTurnCmdFromXAvg(x_avg, x_min, x_max, percents=[]):

	if(not len(percents) == 6):
		# percents = [35,40,45,50,55,60]
		percents = [29,36,43,57,64,71]

	x_max = x_max - x_min
	x_avg = x_avg - x_min
	x_min = 0

	perc = (x_avg*100)/x_max
	
	slow = 100
	med = 120
	medfast = 140
	fast = 160

	if(perc < percents[0]):
		#Hard Left
		return (slow, medfast)
	elif(perc < percents[1]):
		#Left
		return (slow, med)
	elif(perc < percents[2]):
		#Soft Left
		return (slow, slow +10)
	elif(perc < percents[3]):
		#Straight
		return (slow,slow)
	elif(perc < percents[4]):
		#Soft Right
		return (slow +10, slow)
	elif(perc < percents[5]):
		#Right
		return (med, slow)
	else:
		#Hard Right
		return(medfast, slow)

def send_to_arduino(s, cmd):
	s.write((cmd + ".").encode('utf-8'))
	s.flush()

def activate_motors(serial, left, right):
	send_to_arduino(serial, "1 {0} {1}".format(left, right))



s = serial.Serial("/dev/ttyACM0", 115200)

while(True):
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
	    camera.start_preview()
	    #time.sleep(0.1)
	    camera.capture(stream, format='jpeg')
	# "Rewind" the stream to the beginning so we can read its content
	stream.seek(0)
	im = Image.open(stream)

	pix = im.load()
	x, y = im.size

	#Process the image 
	x1, x2, y1, y2 = lineFollowWindow(x,y)
	x_avg, y_avg, num_pos = avgInWindow(pix, x1, x2, y1, y2, isYellow)

	#Based on the data do something
	min_num_pixels = percentToNumPixels(x1, x2, y1, y2, 2)

	left_motor = 0
	right_motor = 0

	if(num_pos > min_num_pixels):
		#results are reliable
		# print("Reliable Results")
		# print(x_avg)
		# getTurnCmdFromXAvg(x_avg, x1, x2)
		#On a linear scale, adjust steering of robot based on x_avg
		left_motor, right_motor = getTurnCmdFromXAvg(x_avg, x1, x2)

	else:
		#results are not reliables
		print("Not Reliable Results")
		# print(x_avg)
		#Rely on something else such as the middle yellow lane
		#Or Search for the line
		#Or make results less sensitive
		left_motor = 85
		right_motor = 130
        
	print(left_motor, right_motor)
	activate_motors(s, left_motor, right_motor)
