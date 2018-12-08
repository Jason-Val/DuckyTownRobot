import time
import picamera
from PIL import Image
import io
import threading
import colorsys

img_sem = threading.Semaphore()
img = None
x_max = 0
y_max = 0
global_error = 0

red = (255,0,0)
white = (255,255,255)
yellow = (255,255,0)


def isColor(color, pixl, diff=250):
    total_diff = abs(pixl[0]-color[0]) + abs(pixl[1]-color[1]) + abs(pixl[2]-color[2])
    if(total_diff < diff):
        return True
    else:
        return False

def isRed(h,l,s):
    if(h > 20.0 and h < 210.0):
        #Hue is not red
        return False
    elif(s < 60.0):
        #Saturation is not good
        return False
    elif(l > 200.0):
        return False
    else:
        return True

def isWhite(h,l,s):
    if(h < 30.0 or h > 45.0 or s < 60.0):
        #Hue is not yellow
        if((h > 20.0 and h < 210.0) or s < 50.0):
            #Hue is not red
            if(l > 180):
                return True
            else:
                return False
        else:
            #Hue is red
            if(l > 200):
                return True
            else:
                return False
    else:
        if(l > 230):
            return True
        else:
            return False

def isYellow(h,l,s):
    if(h < 30.0 or h > 45.0):
        #Hue is not yellow
        return False
    elif(s < 65):
        #Saturation is good
        return False
    elif(l > 210):
        return False
    else:
        return True

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
    num_pix = (x_max-x_min) * (y_max-y_min)
    return (percent/100) * num_pix
    
def lineFollowWindow(x_max, y_max):
    height = int(y_max/6)

    x_start = 0 # Useful for Yellow Line Following
    x_end = x_max

    y_start = int(y_max*0.37)
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
    num_positive = 0
    
    for i in range(int(x_start), int(x_end), int(num_to_process)):
        for j in range(y_start, y_end):
            global img
            h,l,s = colorsys.rgb_to_hls(img[i,j][0]/255.0, img[i,j][1]/255.0, img[i,j][2]/255.0)
            h *= 240.0
            l *= 240.0
            s *= 240.0
            if(isRed(h,l,s)):
                y_avg += j
                num_positive += num_to_process

    req_pixls = percentToNumPixels(x_start, x_end, y_start, y_end, 5)

    if(num_positive > req_pixls and not num_positive == 0):
        y_avg = int(y_avg/num_positive)
        return y_avg
    else:
        return -1

def avgInWindow(x_start, x_end, y_start, y_end, colorFunc, num_to_process=7):
    global img
    img_sem.acquire()
    img_copy = img
    img_sem.release()
    x_avg = 0
    y_avg = 0
    num_positive = 0

    for i in range(x_start, x_end, num_to_process):
        for j in range(y_start, y_end):
            h,l,s = colorsys.rgb_to_hls(img_copy[i,j][0]/255.0, img_copy[i,j][1]/255.0, img_copy[i,j][2]/255.0)
            h *= 240.0
            l *= 240.0
            s *= 240.0
            if(colorFunc(h,l,s)):
                x_avg += i
                y_avg += j
                num_positive += 1

    if(not num_positive == 0):
        x_avg = int(x_avg/num_positive)
        y_avg = int(y_avg/num_positive)

    return (x_avg, y_avg, num_positive*num_to_process)


def ret_error():
    global global_error
    return global_error

def get_error():
    start = time.time()

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
        print("White & Yellow: {}".format(robot_avg - lane_avg + adjust_const))
        print("Processing An Image: {}".format(time.time() - start))
        return robot_avg - lane_avg + adjust_const

    elif(yellow_pos > min_num_pixels and white_pos <= min_num_pixels):
        #Only see Yellow line
        lane_avg = yellow_avg_x + (lane_width_approx_in_pixels/2)
        #print("Case 2 Lane Avg: %s" + str(lane_avg))
        print("Only Yellow: {}".format(robot_avg - lane_avg + adjust_const))
        print("Processing An Image: {}".format(time.time() - start))
        return robot_avg - lane_avg + adjust_const

    elif(yellow_pos <= min_num_pixels and white_pos > min_num_pixels):
        #Only see White line
        lane_avg = white_avg_x - (lane_width_approx_in_pixels/2)
        #print("Case 3 Lane Avg: %s" + str(lane_avg))
        print("Only White: {}".format(robot_avg - lane_avg + adjust_const))
        print("Processing An Image: {}".format(time.time() - start))
        return robot_avg - lane_avg + adjust_const

    else:
        print("No Yellow Or White")
        print("Processing An Image: {}".format(time.time() - start))
        return None
    
"""
Constantly streams video
"""
def start_thread():
    global img
    global x_max
    global y_max
    global global_error
    with picamera.PiCamera() as camera:
        camera.start_preview()
        stream = io.BytesIO()
        camera.framerate = 10
        time.sleep(2)
        for foo in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
            start = time.time()
            stream.truncate()
            stream.seek(0)
            im = Image.open(stream)
            x_max, y_max = im.size
            pix = im.load()
            img_sem.acquire()
            img = pix
            img_sem.release()
            print()
            print("Image Loading: {}".format(time.time() - start))
            start = time.time()
            # global_error = get_error()
            print("Image Processing: {}".format(time.time() - start))
            print()
        camera.end_preview()