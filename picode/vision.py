import time
import picamera
from PIL import Image
import io
import threading
"""

y: [143, 384], 5894
w: [1246, 383], 2024
------
0
y: [0, 0], 0
w: [1259, 384], 2283
------
0
y: [158, 386], 5877
w: [1259, 383], 2136
------
0
y: [150, 389], 7004
w: [1238, 384], 2278
------
0
y: [150, 389], 7030
w: [1239, 384], 2283
------
0
y: [150, 389], 7037
w: [1235, 384], 2299
------
0
y: [151, 389], 6941
w: [1237, 384], 2287
------
0
y: [150, 389], 6998
w: [1240, 384], 2280
------
0
y: [150, 389], 7022
w: [1241, 384], 2278
------
0
y: [152, 388], 6758
w: [1248, 384], 2234
------
0
y: [243, 381], 5262
w: [0, 0], 0
------
0
y: [211, 389], 7091
w: [1278, 361], 10
------
0
y: [210, 389], 7096
w: [1278, 361], 10
------
0
y: [210, 389], 7114
w: [1278, 361], 10
------
0
y: [145, 399], 8634
w: [1253, 390], 3579
------
0
y: [25, 385], 2980
w: [1184, 407], 19191
------
0
y: [25, 386], 3136
w: [1184, 407], 19175
------
0
y: [25, 386], 3139
w: [1184, 407], 19168
------
0
y: [25, 387], 3191
w: [1184, 407], 19175
------
0
y: [28, 387], 3452
w: [1196, 406], 16720
------
0
y: [314, 384], 4359
w: [237, 424], 467
------
0
y: [315, 384], 4394
w: [242, 419], 560
------
0
y: [316, 383], 4318
w: [242, 419], 557
------
0
y: [312, 385], 4521
w: [274, 381], 100
------
0
y: [896, 389], 1621
w: [852, 401], 3874
------
0
y: [0, 360], 2
w: [1147, 409], 23726
------
0
y: [0, 0], 0
w: [1144, 409], 23991
------
0
y: [0, 0], 0
w: [1144, 409], 24001
------
0
y: [30, 388], 4036
w: [1195, 406], 16835
------
0
y: [65, 386], 6266
w: [1216, 404], 11705

"""
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
    
    """
    if (yellow_pos > min_num_pixels):
        #calculate center based on yellow position
    if (white_pos > min_num_pixels):
        #calculate center based on white position
    
    
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
    return 0
    
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