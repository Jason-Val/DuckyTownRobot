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
robot = None

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

def isGreenLight(h,l,s):
    if(h < 40.0 or h > 105.0):
        #Hue is not green
        return False
    elif(l < 145):
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

    y_start = int(y_max*0.3)
    y_end = y_start + height

    return(x_start, x_end, y_start, y_end)

def stopWindow():
    height = int(y_max/2)

    global x_max

    x_start = x_max*0.45 # Useful for Yellow Line Following
    x_end = x_max*0.55

    y_start = int(y_max*0.55)
    y_end = y_start + height
    
    if(y_end > y_max):
        y_end = y_max

    return(x_start, x_end, y_start, y_end)

def greenLightWindow():
    # height = int(y_max/5)

    x_start = x_max*0.3 # Useful for Yellow Line Following
    x_end = x_max*0.7

    y_start = y_max*0.5
    y_end = y_max*1.0

    return(x_start, x_end, y_start, y_end)

def saw_green_light(num_to_process_x=7, num_to_process_y=7):
    x_start, x_end, y_start, y_end = greenLightWindow()
    # return True
    num_positive = 0
    
    for i in range(int(x_start), int(x_end), int(num_to_process_x)):
        for j in range(int(y_start), int(y_end), int(num_to_process_y)):
            global img
            h,l,s = colorsys.rgb_to_hls(img[i,j][0]/255.0, img[i,j][1]/255.0, img[i,j][2]/255.0)
            h *= 240.0
            l *= 240.0
            s *= 240.0
            if(isGreenLight(h,l,s)):
                num_positive += num_to_process_x*num_to_process_y

    req_pixls = percentToNumPixels(x_start, x_end, y_start, y_end, 0.2)

    if(num_positive > req_pixls and not num_positive == 0):
        return True
    else:
        return False

def isStopSign(num_to_process_x=12, num_to_process_y=12):
    x_start, x_end, y_start, y_end = stopWindow()

    y_avg = 0
    num_positive = 0
    
    for i in range(int(x_start), int(x_end), int(num_to_process_x)):
        for j in range(int(y_start), int(y_end), int(num_to_process_y)):
            global img
            h,l,s = colorsys.rgb_to_hls(img[i,j][0]/255.0, img[i,j][1]/255.0, img[i,j][2]/255.0)
            h *= 240.0
            l *= 240.0
            s *= 240.0
            if(isRed(h,l,s)):
                y_avg += j
                num_positive += 1

    req_pixls = percentToNumPixels(x_start, x_end, y_start, y_end, 3)

    if(num_positive*num_to_process_x*num_to_process_y > req_pixls and not num_positive == 0):
        y_avg = int(y_avg/num_positive)
        #print("------ Saw the stop sign {}".format(y_avg))
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

def whiteAndYellowXAvgsInWindow(x_start, x_end, y_start, y_end, num_to_process_x=7, num_to_process_y=7):
    global img
    img_sem.acquire()
    img_copy = img
    img_sem.release()

    x_avg_w = 0
    num_positive_w = 0
    x_avg_y = 0
    num_positive_y = 0
    

    for i in range(x_start, x_end, num_to_process_x):
        for j in range(y_start, y_end, num_to_process_y):
            h,l,s = colorsys.rgb_to_hls(img_copy[i,j][0]/255.0, img_copy[i,j][1]/255.0, img_copy[i,j][2]/255.0)
            h *= 240.0
            l *= 240.0
            s *= 240.0

            if(isWhite(h,l,s)):
                x_avg_w += i
                num_positive_w += 1
            if(isYellow(h,l,s)):
                x_avg_y += i
                num_positive_y += 1

    if(not num_positive_w == 0):
        x_avg_w = int(x_avg_w/num_positive_w)
    if(not num_positive_y == 0):
        x_avg_y = int(x_avg_y/num_positive_y)

    return [(x_avg_w, num_positive_w*num_to_process_x*num_to_process_y), (x_avg_y, num_positive_y*num_to_process_x*num_to_process_y)]


def ret_error():
    global global_error
    return global_error

def get_error():

    global img
    global x_max
    global y_max

    adjust_const = 0

    x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
    avgs_tuple = whiteAndYellowXAvgsInWindow(x_start, x_end, y_start, y_end)
    white_avg_x, white_pos = avgs_tuple[0]
    yellow_avg_x, yellow_pos = avgs_tuple[1]

    min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 1)
    incr = x_max/100

    lane_width_approx_in_pixels = 850

    robot_avg = x_max/2
    #print("Robot Avg: %s" + str(robot_avg))

    lane_avg = 0

    if(yellow_pos > min_num_pixels and white_pos > min_num_pixels):
        #We see both the yellow and white line
        #This is the case we want
        if(white_avg_x < yellow_avg_x or abs(white_avg_x - yellow_avg_x) < 80):
            #In this case it likely saw a glare and detected it as white
            #Or, it saw the wrong white (White is on the left) line and tried to take the middle
            #White is unreliable
            lane_avg = yellow_avg_x + (lane_width_approx_in_pixels/2)
            #print("White & Yellow (Warn) -> Yellow: {}".format(lane_avg))
        else:
            lane_avg = (white_avg_x + yellow_avg_x)/2
            # print(white_avg_x)
            # print(yellow_avg_x)
            #print("White & Yellow: {}".format(lane_avg))

    elif(yellow_pos > min_num_pixels and white_pos <= min_num_pixels):
        #Only see Yellow line
        lane_avg = yellow_avg_x + (lane_width_approx_in_pixels/2 + 100)
        #print("Case 2 Lane Avg: %s" + str(lane_avg))
        #print("Only Yellow: {}".format(robot_avg - lane_avg + adjust_const))

    elif(yellow_pos <= min_num_pixels and white_pos > min_num_pixels):
        #Only see White line
        lane_avg = white_avg_x - (lane_width_approx_in_pixels/2 + 100)
        #print("Case 3 Lane Avg: %s" + str(lane_avg))
        #print("Only White: {}".format(robot_avg - lane_avg + adjust_const))

    else:
        #print("No Yellow Or White")
        return None

    return robot_avg - lane_avg + adjust_const
    
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
        camera.resolution = (1024, 768)
        time.sleep(2)
        while(robot.active):
            stream = io.BytesIO()
            camera.capture(stream, format='jpeg', use_video_port=True)
            stream.seek(0)
            im = Image.open(stream)
            x_max, y_max = im.size
            pix = im.load()
            img_sem.acquire()
            img = pix
            img_sem.release()
        camera.stop_preview()