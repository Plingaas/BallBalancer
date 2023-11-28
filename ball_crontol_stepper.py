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
camera_port = 0
cap = cv2.VideoCapture(camera_port)
cap.set(3, 1280)
cap.set(4, 720)

get, img = cap.read()
h, w, _ = img.shape

port_id = '/dev/cu.usbserial-110'
# initialise serial interface
arduino = serial.Serial(port=port_id, baudrate=230400, timeout=0.1)

# define servo angles and set a value
servo1_angle = 0
servo2_angle = 0
servo3_angle = 0
all_angle = 0

# Set a limit to upto which you want to rotate the servos (You can do it according to your needs)
servo1_angle_limit_positive = 90
servo1_angle_limit_negative = -90

servo2_angle_limit_positive = 90
servo2_angle_limit_negative = -90

servo3_angle_limit_positive = 90
servo3_angle_limit_negative = -90

maxpitch = 16.5
maxroll = 15
target = Position()
center_point = [640, 360, 2210] # center point of the plate, calibrated

def ball_track(key1, queue):

    if key1:
        print('Ball tracking is initiated')

    myColorFinder = ColorFinder(False)  # if you want to find the color and calibrate the program we use this *(Debugging)
    hsvVals = {'hmin': 0, 'smin': 240, 'vmin': 162, 'hmax': 180, 'smax': 255, 'vmax': 255}

    #center_point = [626, 337, 2210] # center point of the plate, calibrated
    global center_point
    while True:
        get, img = cap.read()
        imgColor, mask = myColorFinder.update(img, hsvVals)
        imgContour, countours = cvzone.findContours(img, mask)

        x = 0
        y = 0
        if countours:
            x = round(countours[0]['center'][0])
            y = round(countours[0]['center'][1])
            data = round((countours[0]['center'][0] - center_point[0])), \
                   round((h - countours[0]['center'][1] - center_point[1])), \
                   round(int(countours[0]['area'] - center_point[2])/100)

            queue.put(data)
            #print("The got coordinates for the ball are :", data)
        else:
            data = 'nil' # returns nil if we cant find the ball
            queue.put(data)

        imgStack = cvzone.stackImages([imgContour], 1, 1)
        #imgStack = cvzone.stackImages([img,imgColor, mask, imgContour],2,0.5) #use for calibration and correction
        cv2.circle(imgStack, (x, y), 290, (255, 255, 255), 2)
        cv2.circle(imgStack, (x, y), 30, (255, 255, 255), 1)
        cv2.circle(imgStack, (center_point[0], center_point[1]), 290, (255, 0, 255), 2)
        cv2.circle(imgStack, (center_point[0], center_point[1]), 30, (255, 0, 255), 1)

        cv2.circle(imgStack, (center_point[0]+target.target[0],center_point[1]+target.target[1]), 5, (0, 0, 255), -1)
        cv2.imshow("Image", imgStack)
        cv2.waitKey(1)

start = time.time()
prevTime = time.time()
lastX = 999
lastY = 999
def servo_control(key2, queue):
    if key2:
        print('Servo controls are initiated')


    def all_angle_assign(angle_passed1,angle_passed2,angle_passed3):
        global servo1_angle, servo2_angle, servo3_angle
        servo1_angle = math.radians(float(angle_passed1))
        servo2_angle = math.radians(float(angle_passed2))
        servo3_angle = math.radians(float(angle_passed3))
        write_servo()

    root = Tk()
    root.resizable(0, 0)

    def writeCoord():
        """
        Here in this function we get both coordinate and servo control, it is an ideal place to implement the controller
        """
        global lastX
        global lastY
        coords = queue.get()
        # Time
        global prevTime
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
            ang1 = int(round(angles[0]+30))
            ang2 = int(round(angles[1]+30))
            ang3 = int(round(angles[2]+30))

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

    def write_arduino(data):
        #print('The angles send to the arduino : ', data)

        arduino.write(bytes(data, 'utf-8'))

    def write_servo():
        ang1 = servo1_angle
        ang2 = servo2_angle
        ang3 = servo3_angle

        angles: tuple = (round(math.degrees(ang1), 1),
                         round(math.degrees(ang2), 1),
                         round(math.degrees(ang3), 1))

        write_arduino(str(angles))

    while key2:
        writeCoord()

    root.mainloop()  # running loop

if __name__ == '__main__':

    queue = Queue() # The queue is done inorder for the communication between the two processes.
    key1 = 1 # just two dummy arguments passed for the processes
    key2 = 2
    p1 = mp.Process(target= ball_track, args=(key1, queue)) # initiate ball tracking process
    p2 = mp.Process(target=servo_control,args=(key2, queue)) # initiate servo controls
    p1.start()
    p2.start()
    p1.join()
    p2.join()

# Close the file when the program is done
logger.close_file()