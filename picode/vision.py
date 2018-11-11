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
    global img

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

def percentToNumPixels(x_min, x_max, y_min, y_max, percent):
    num_pix = (x_max-x_min) * (y_max-y_min)
    return (percent/100) * num_pix

"""

"""
def get_error():
    #Do This
    global x_max
    global y_max
    global img_sem
    
    left_lane_ideal = 150
    right_lane_ideal = 1259
    
    hard_right = (125,0)
    right = (145,110)
    soft_right = (140,125)
    straight = (130,130)
    soft_left = (125,140)
    left = (110,145)
    hard_left = (0,125)
    
    x_start, x_end, y_start, y_end = lineFollowWindow(x_max, y_max)
    img_sem.acquire()
    yellow_avg_x, yellow_y, yellow_pos = avgInWindow(x_start, x_end, y_start, y_end, isYellow)
    white_avg_x, white_y, white_pos = avgInWindow(x_start, x_end, y_start, y_end, isWhite)
    img_sem.release()
    
    min_num_pixels = percentToNumPixels(x_start, x_end, y_start, y_end, 1)
    
    print("y: [{0}, {1}], {2}".format(yellow_avg_x, yellow_y, yellow_pos))
    print("w: [{0}, {1}], {2}".format(white_avg_x, white_y, white_pos))
    print("------")
    
    error = 0
    
    left_error = 0
    right_error = 0
    
    if (yellow_pos > min_num_pixels):
        #calculate center based on yellow position
        left_error = left_lane_ideal - yellow_avg_x #positive if too far left
    if (white_pos > min_num_pixels):
        #calculate center based on white position
        right_error = right_lane_ideal - white_avg_x #positive if too far left
    
    print("left error: {}; right error: {}".format(left_error, right_error))
    return left_error
    """
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
    """
    
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