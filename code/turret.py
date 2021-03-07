#INIT----------------------------#
import numpy as np,cv2,time,configparser
config = configparser.ConfigParser()
config.read('config.ini')
#GPIO SETUP----------------------#
import RPi.GPIO as GPIO
pinnums = [29,31]
GPIO.setmode(GPIO.BOARD)
for _ in pinnums:
    GPIO.setup(_,GPIO.OUT)
servo1=GPIO.PWM(pinnums[0],50);servo2=GPIO.PWM(pinnums[1],50);servo1.start(0);servo2.start(0)
servo1.ChangeDutyCycle(6);servo2.ChangeDutyCycle(6);time.sleep(1)
#CONFIG--------------------------#
#servo
pan_angle = config['servos']['pan_angle']
tilt_angle = config['servos']['tilt_angle']
increment = config['servos']["increment"]
pan_home = config['servos']["pan_home"]
tilt_home = config['servos']["tilt_home"]
#cv
res_width = config['opencv']["res_width"]
res_height = config['opencv']["res_height"]
window_name = config["opencv"]["window_name"]
camera_number = config["opencv"]["camera_number"]
fps = config["opencv"]["fps"]
#CV setup-----------------------#
cap = cv2.VideoCapture(camera_number)
cap.set(cv2.CAP_PROP_FPS,fps)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, res_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res_height)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#Program------------------------#
def align(frame,x,y,width,height):
    global pan_angle,tilt_angle
    #TILT
    tilt_bound = height/20
    lbt = height/2-tilt_bound
    ubt = height/2+tilt_bound
    tilt = True
    pan = True
    if lbt<y and y<ubt:
        tilt=False
    elif y<lbt and tilt == True:
        tilt_angle+=increment
        if tilt_angle>=180:
            tilt_angle= tilt_home
    elif x>lbt and tilt==True:
        tilt_angle-=increment
        if tilt_angle<=0:
            tilt_angle=tilt_home
    #PAN
    pan_bound = width/20
    lbp = width/2-pan_bound
    ubp = width/2+pan_bound
    if lbp<x and x<ubp:
        pan=False
    elif x<lbp and pan==True:
        pan_angle+=increment
        if pan_angle>=180:
            pan_angle=pan_home
    elif x>lbp and pan==True:
        pan_angle-=increment
        if pan_angle<=0:
            pan_angle=pan_home
    cv2.putText(frame,str(pan_angle)+" "+str(tilt_angle),(100,200),cv2.FONT_HERSHEY_DUPLEX,1,(0,0,0),3)

         
ret, frame = cap.read()
height, width = frame.shape[0:2]
pixel_degree_x,pixel_degree_y = (abs((width/180)/2),abs((height/180)/2))
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        #Find center distance
        center = (int(x+(.5*w)),int(y+.5*h))
        distance_center_x = center[0]-(width/2)
        distance_center_y = (height/2)-center[1]
        #Motor Logic
        align(frame,center[0],center[1],width,height) #returns pan angle, tilt angle
        x_duty_conversion = 2+(pan_angle/18);y_duty_conversion = 2+(pan_angle/18)
        servo1.ChangeDutyCycle(x_duty_conversion);servo2.ChangeDutyCycle(y_duty_conversion)
        #Drawing
        cv2.putText(frame,str(distance_center_x)+" | "+str(distance_center_y),(center[0]+100,center[1]-100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        cv2.line(frame, (center[0],0),(center[0],height),(0,0,255), 5)
        cv2.line(frame, (0,center[1]),(width,center[1]),(0,0,255), 5)
        cv2.putText(frame,str(center),(center[0]-200,center[1]+50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        cv2.putText(frame,"No faces",(100,100),cv2.FONT_HERSHEY_DUPLEX,1,(0,0,0),3)
    cv2.imshow(window_name, frame)
    if cv2.waitKey(1) == ord('q'):
        servo1.stop()
        servo2.stop()
        GPIO.cleanup()
        break

cap.release()
cv2.destroyAllWindows()
