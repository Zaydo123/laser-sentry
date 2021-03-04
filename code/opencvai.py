import numpy as np
import cv2
#import RPi.GPIO as GPIO
import time
#pinnums = [29,31]
#GPIO.setmode(GPIO.BOARD)
#for _ in pinnums:
#    GPIO.setup(_,GPIO.OUT)
#servo1=GPIO.PWM(pinnums[0],50)
#servo2=GPIO.PWM(pinnums[1],50)
#servo1.start(0)
#servo2.start(0)
#servo1.ChangeDutyCycle(2)
#servo2.ChangeDutyCycle(2)
#time.sleep(1)
cap = cv2.VideoCapture(0)
countingint = 0
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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
try:
    ret, frame = cap.read()
    height, width = frame.shape[0:2]
    pixel_degree_x,pixel_degree_y = (width/180,height/180)
    degrees_x = 0
    while True:
        ret, frame = cap.read()
        cv2.resize(frame,(width,height))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        #centerlines (performance decrease)
        #cv2.line(frame,(int(width/2),0),(int(width/2),height),(255,0,0),1)
        #cv2.line(frame,(0,int(height/2)),(width,int(height/2)),(255,0,0),1)
        cv2.putText(frame,"X|Y Pixel/degree conversion",(100,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
        cv2.putText(frame,str(pixel_degree_x)+" | "+str(pixel_degree_y),(100,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),3)
        for (x, y, w, h) in faces:
            #find center of face and distance from center of camera
            center = (int(x+(.5*w)),int(y+.5*h))
            cv2.line(frame, (center[0],0),(center[0],height),(0,0,255), 5)
            cv2.line(frame, (0,center[1]),(width,center[1]),(0,0,255), 5)
            cv2.putText(frame,str(center),(center[0]-200,center[1]+50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
            distance_center_x = center[0]-(width/2)
            distance_center_y = (height/2)-center[1]
            quadrant = find_quadrant(distance_center_x,distance_center_y)
            cv2.putText(frame,str(distance_center_x)+" | "+str(distance_center_y)+" | Q"+str(quadrant),(center[0]+100,center[1]-100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
            x_movement = 90+(distance_center_x/pixel_degree_x)
            y_movement = 90+(distance_center_y/pixel_degree_y)
            print((x_movement,y_movement))
            #motor movement logic
            #Notes:
            #home position of x axis servo should be 90 degrees > 180/2 = 90
            #home of y doesn't matter, 90 should be fine
            #90+(distance/pixel to degree conversion rate) should = rotation of servos?

        cv2.imshow('BBSCK', frame)
        if cv2.waitKey(1) == ord('q'):
            #servo1.stop()
            #servo2.stop()
            #GPIO.cleanup()
            print('done')
            break

except ValueError:
    print("VAL ERR")

cap.release()
cv2.destroyAllWindows()
