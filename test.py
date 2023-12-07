from glob import glob
from hashlib import new
import multiprocessing as mp
from multiprocessing import Queue
import cvzone
from cvzone.ColorModule import ColorFinder
import cv2
import serial
import math
from tkinter import *
from ik import *
from pid import *
import time
from pos import *
from logger import *

# -------------------------------------------Both programs(Servo Control and Ball Tracker) in one -------------------------------------------
"""
For running both programs simultaneously we can use multithreading or multiprocessing
"""
logger = RealTimeLogger()

PIDX = PID()
PIDY = PID()
# Create a figure and axis
camera_port = 0
cap = cv2.VideoCapture(camera_port)
cap.set(3, 1280)
cap.set(4, 720)

get, img = cap.read()
h, w, _ = img.shape

port_id = '/dev/cu.usbserial-120' 
# initialise serial interface
arduino = serial.Serial(port=port_id, baudrate=230400, timeout=0.1)


maxpitch = 16.5
maxroll = 15
target = Position()
center_point = [640, 380, 2210] # center point of the plate, calibrated
traces = []

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        target.target = (x-center_point[0], -y+center_point[1]-40)

cv2.namedWindow('Image')
cv2.setMouseCallback('Image', mouse_callback)

prevTime = time.time()
start = time.time()
lastX = 999
lastY = 999

if __name__ == "__main__":
    while True:
        myColorFinder = ColorFinder(False)  # if you want to find the color and calibrate the program we use this *(Debugging)
        hsvVals = {'hmin': 0, 'smin': 230, 'vmin': 162, 'hmax': 180, 'smax': 255, 'vmax': 255}

        get, img = cap.read()
        imgColor, mask = myColorFinder.update(img, hsvVals)
        imgContour, countours = cvzone.findContours(img, mask)

        x = 0
        y = 0
        rx = 0
        ry = 0
        if countours:
            x = round(countours[0]['center'][0])
            y = round(countours[0]['center'][1])
            data = round((countours[0]['center'][0] - center_point[0])), \
                    round((h - countours[0]['center'][1] - center_point[1])), \
                    round(int(countours[0]['area'] - center_point[2])/100)
            #print("The got coordinates for the ball are :", data)
        else:
            data = 'nil' # returns nil if we cant find the ball

        imgStack = cvzone.stackImages([imgContour], 1, 1)
        cv2.circle(imgStack, (x, y), 290, (255, 255, 255), 2)
        cv2.circle(imgStack, (x, y), 30, (255, 255, 255), 1)
        cv2.circle(imgStack, (center_point[0], center_point[1]-40), 290, (255, 0, 255), 2)
        cv2.circle(imgStack, (center_point[0], center_point[1]-40), 30, (255, 0, 255), 1)

        cv2.imshow("Image", imgStack)
        cv2.waitKey(1)

        coords = data
        dt = time.time() - prevTime
        prevTime += dt
        target.update(dt)
        if coords == 'nil': # Checks if the output is nil
            print('Can\'t find the ball.')
            PIDX.prevError = 0
            PIDX.prevIntegral = 0
            PIDY.prevError = 0
            PIDY.prevIntegral = 0
            lastY = 999
            lastX = 999

        else:
            # PID

            reg_x = PIDX.regulate(target.target[0], coords[0], dt)
            new_x = reg_x
        
            reg_y = PIDY.regulate(target.target[1], coords[1], dt)
            new_y = reg_y

            # IK
            pitch = new_y/2.0
            roll = new_x/2.0

            if (pitch > maxpitch):
                pitch = maxpitch
            if (pitch < -maxpitch):
                pitch = -maxpitch
            
            if (roll > maxpitch):
                roll = maxpitch
            if (roll < -maxpitch):
                roll = -maxpitch

            pitch = -np.deg2rad(pitch)
            roll = -np.deg2rad(roll)
            
            angles = getAngles(pitch, roll)
            ang1 = angles[0]+32
            ang2 = angles[1]+28
            ang3 = angles[2]+29.6

            intang1 = int(ang1)
            intang2 = int(ang2)
            intang3 = int(ang3)
            fang1 = int((ang1-intang1)*256)
            fang2 = int((ang2-intang2)*256)
            fang3 = int((ang3-intang3)*256)
            
            angles = bytearray([intang1, fang1, intang2, fang2, intang3, fang3])
            if (ang1 >= 5 and ang2 >= 5 and ang3 >= 5):
                arduino.write(angles)
            
            velx = float(new_x - lastX)/dt
            vely = float(new_y - lastY)/dt

            time_ms = round((time.time()-start)*1000)
            data = (time_ms, 
                    coords[0], 
                    coords[1],
                    velx,
                    vely,
                    pitch, 
                    roll, 
                    target.target[0], 
                    target.target[1])
            logger.log_data(*data)
            lastX = new_x
            lastY = new_y

# Close the file when the program is done
logger.close_file()