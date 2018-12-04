import time
import picamera
from PIL import Image
import io
import threading
import colorsys\

img  = None
x_max = 0
y_max = 0

def start_thread():
    global img
    global x_max
    global y_max
    # global global_error

    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        while(True):
            start1 = time.time()
            start = time.time()
            stream = io.BytesIO()
            print("Stream = Bytes: {}".format(time.time() - start))
            start = time.time()
            camera.capture(stream, format='jpeg')
            print("Capture: {}".format(time.time() - start))
            start = time.time()
            stream.seek(0)
            print("Seek: {}".format(time.time() - start))
            start = time.time()
            im = Image.open(stream)
            print("Open: {}".format(time.time() - start))
            start = time.time()
            x_max, y_max = im.size
            print("Size: {}".format(time.time() - start))
            start = time.time()
            pix = im.load()
            print("---LOAD---: {}".format(time.time() - start))
            start = time.time()
            img_sem.acquire()
            # start = time.time()
            img = pix
            print("set Global: {}".format(time.time() - start))
            # global_error = get_error()
            # img_sem.release()
            print("Loading In An Image: {}".format(time.time() - start1))
        camera.end_preview()

start_thread()