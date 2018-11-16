import time
import picamera
from PIL import Image
import io
import threading

img_sem = threading.Semaphore()
img = None
x_max = 0
y_max = 0

white_hsv = (80, 37, 0, 100, 75, 100)
yellow_hsv = (18,81,12,100,22,100)
red = (255,0,0)
white = (255,255,255)
yellow = (255,255,0)


def isColor(color, pixl, diff=250):
    total_diff = abs(pixl[0]-color[0]) + abs(pixl[1]-color[1]) + abs(pixl[2]-color[2])
    if(total_diff < diff):
        return True
    else:
        return False

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx       
    v = mx
    return h, s*100, v*100

def isHSVColor(color, pixl):
    h,s,v = rgb2hsv(pixl[0],pixl[1],pixl[2])
    if(color[0]<=color[1] and h >= color[0] and h <= color[1] and s >= color[2] and s <= color[3] and v >= color[4] and v <= color[5]):
        return True
    elif((h >= color[0] or h <= color[1]) and s >= color[2] and s <= color[3] and v >= color[4] and v <= color[5]):
        return True
    else:
        return False

def isRed(pixl):
    return isColor(red, pixl)

def isWhite(pixl):
    return isHSVColor(white_hsv, pixl)

def isYellow(pixl):
    return isHSVColor(yellow_hsv, pixl)

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
    num_pix = (x_max-x_min) * (y_max-y_min)
    return int((percent/100) * num_pix)
    
def lineFollowWindow(x_max, y_max):
    height = int(y_max/6)

    x_start = 0 # Useful for Yellow Line Following
    x_end = x_max

    y_start = int(y_max*0.32)
    y_end = y_start + height

    return(x_start, x_end, y_start, y_end)

def stopWindow():
    height = int(y_max/2)

    global x_max

    x_start = int(x_max*0.4) # Useful for Yellow Line Following
    x_end = int(x_max*0.6)

    y_start = int(y_max*0.5)
    y_end = y_start + height

    return(x_start, x_end, y_start, y_end)

def isStopSign(num_to_process=50):
    x_start, x_end, y_start, y_end = stopWindow()

    y_avg = 0
    num_positive = 0

    for i in range(x_start, x_end, int(num_to_process)):
        for j in range(y_start, y_end):
            global img
            if(isRed(img[i,j])):
                y_avg += j
                num_positive += num_to_process

    req_pixls = percentToNumPixels(x_start, x_end, y_start, y_end, 3)

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

    str_time = time.time()

    global img
    global x_max
    global y_max
    
    #Going up goes to the left by a matter on pixels
    adjust_const = 45

    x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
    yellow_avg_x, yellow_y, yellow_pos = avgInWindow(x_start, x_end, y_start, y_end, isYellow)
    white_avg_x, white_y, white_pos = avgInWindow(x_start, x_end, y_start, y_end, isWhite)

    min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 2)
    incr = x_max/100

    lane_width_approx_in_pixels = 1000

    robot_avg = x_max/2
    #print("Robot Avg: %s" + str(robot_avg))

    print("Im Processing Took: " + str(time.time() - str_time))

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
