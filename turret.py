import numpy as np
import cv2
import time
import RPi.GPIO as GPIO
pinnums = [29,31]
GPIO.setmode(GPIO.BOARD)
for _ in pinnums:
    GPIO.setup(_,GPIO.OUT)
servo1=GPIO.PWM(pinnums[0],50)
servo2=GPIO.PWM(pinnums[1],50)
servo1.start(0)
servo2.start(0)
servo1.ChangeDutyCycle(6)
servo2.ChangeDutyCycle(6)
time.sleep(1)
servo1.ChangeDutyCycle(0)
servo2.ChangeDutyCycle(0)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS,60)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
pan_angle = 0

def find_quadrant(x,y):
    if x>=0: xpos = True
    else:xpos = False
    if y>=0: ypos = True
    else:ypos=False
    if xpos==False and ypos==True:
        return 1
    elif xpos==True and ypos==True:
        return 2
    elif xpos==False and ypos==False:
        return 3
    elif xpos==True and ypos==False:
        return 4

def is_centered(x,width):
    global pan_angle
    bound = (width/20)
    lower_bound = (width/2)-bound
    upper_bound = (width/2)+bound
    if (width/2)-bound<x and x<(width/2)+bound:
        return True
    elif x<lower_bound:
        pan_angle= pan_angle+5
        if pan_angle>=180:
            pan_angle=90 #resetting to 90 degrees (home) if can't move further
    elif x>lower_bound:
        pan_angle= pan_angle-5
        if pan_angle<=0:
            pan_angle=90
    return pan_angle

         
ret, frame = cap.read()
height, width = frame.shape[0:2]
pixel_degree_x,pixel_degree_y = (abs((width/180)/2),abs((height/180)/2))
while True:
    ret, frame = cap.read()
    #cv2.resize(frame,(width,height))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        #find center of face and distance from center of camera
        center = (int(x+(.5*w)),int(y+.5*h))
        #cv2.line(frame, (center[0],0),(center[0],height),(0,0,255), 5)
        #cv2.line(frame, (0,center[1]),(width,center[1]),(0,0,255), 5)
        #cv2.putText(frame,str(center),(center[0]-200,center[1]+50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        distance_center_x = center[0]-(width/2)
        distance_center_y = (height/2)-center[1]
        #quadrant = find_quadrant(distance_center_x,distance_center_y)
        #cv2.putText(frame,str(distance_center_x)+" | "+str(distance_center_y)+" | Q"+str(quadrant),(center[0]+100,center[1]-100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        is_centered(center[0],width)
        x_duty_conversion = 2+(pan_angle/18)
        servo1.ChangeDutyCycle(x_duty_conversion)
        time.sleep(.1)
    if len(faces)==0:
        servo1.ChangeDutyCycle(6)
        #time.sleep(.1)
        #servo1.ChangeDutyCycle(0)
        #time.sleep(.1)
    cv2.imshow('BBSCK', frame)
    if cv2.waitKey(1) == ord('q'):
        servo1.stop()
        servo2.stop()
        GPIO.cleanup()
        print('done')
        break

cap.release()
cv2.destroyAllWindows()
