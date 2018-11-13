import time
import picamera
from PIL import Image
import io
import threading

img_sem = threading.Semaphore()
img = None
x_max = 0
y_max = 0

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

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
    num_pix = (x_max-x_min) * (y_max-y_min)
    return (percent/100) * num_pix
    
def lineFollowWindow(x_max, y_max):
    height = int(y_max/7)

    x_start = 0 # Useful for Yellow Line Following
    x_end = x_max

    y_start = int(y_max*0.5)
    y_end = y_start + height

    return(x_start, x_end, y_start, y_end)

def stopWindow():
    height = int(y_max/2)

    global x_max

    x_start = x_max*0.4 # Useful for Yellow Line Following
    x_end = x_max*0.6

    y_start = int(y_max*0.5)
    y_end = y_start + height

    return(x_start, x_end, y_start, y_end)

def isStopSign(num_to_process=10):
    x_start, x_end, y_start, y_end = stopWindow()

    y_avg = 0

    for i in range(x_start, x_end, num_to_process):
        for j in range(y_start, y_end):
            global img
            if(isRed(img[i,j])):
                y_avg += j
                num_positive += num_to_process

    req_pixls = percentToNumPixels(x_start, x_end, y_start, y_end, 5)

    if(num_positive > req_pixls and not num_positive == 0):
        y_avg = int(y_avg/num_positive)
        return y_avg
    else:
        return -1

def avgInWindow(x_start, x_end, y_start, y_end, colorFunc, num_to_process=10):
    x_avg = 0
    y_avg = 0
    num_positive = 0

    for i in range(x_start, x_end, num_to_process):
        for j in range(y_start, y_end):
            global img
            if(colorFunc(img[i,j])):
                x_avg += i
                y_avg += j
                num_positive += 1

    if(not num_positive == 0):
        x_avg = int(x_avg/num_positive)
        y_avg = int(y_avg/num_positive)

    return (x_avg, y_avg, num_positive*num_to_process)

"""

"""
def get_error():

    global img
    global x_max
    global y_max

    adjust_const = 15

    x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
    yellow_avg_x, yellow_y, yellow_pos = avgInWindow(x_start, x_end, y_start, y_end, isYellow)
    white_avg_x, white_y, white_pos = avgInWindow(x_start, x_end, y_start, y_end, isWhite)

    min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 1)
    incr = x_max/100

    lane_width_approx_in_pixels = 1000

    robot_avg = x_max/2
    #print("Robot Avg: %s" + str(robot_avg))

    if(yellow_pos > min_num_pixels and white_pos > min_num_pixels):
        #We see both the yellow and white line
        #This is the case we want
        lane_avg = (white_avg_x + yellow_avg_x)/2
        #print("Case 1 Lane Avg: %s" + str(lane_avg))
        return robot_avg - lane_avg + adjust_const

    elif(yellow_pos > min_num_pixels and white_pos <= min_num_pixels):
        #Only see Yellow line
        lane_avg = yellow_avg_x + (lane_width_approx_in_pixels/2)
        #print("Case 2 Lane Avg: %s" + str(lane_avg))
        return robot_avg - lane_avg + adjust_const

    elif(yellow_pos <= min_num_pixels and white_pos > min_num_pixels):
        #Only see White line
        lane_avg = white_avg_x - (lane_width_approx_in_pixels/2)
        #print("Case 3 Lane Avg: %s" + str(lane_avg))
        return robot_avg - lane_avg + adjust_const

    else:
        print("No Yellow Or White")
        return None
    
"""
Constantly streams video
"""
def start_thread():
    global img
    global x_max
    global y_max
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        while(True):
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg')
            stream.seek(0)
            im = Image.open(stream)
            x_max, y_max = im.size
            pix = im.load()
            img_sem.acquire()
            img = pix
            img_sem.release()
        camera.end_preview()