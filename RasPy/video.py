import cv2
import sys, os, time, datetime

os.environ["DISPLAY"]=":0"

faceCascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier('/home/pi/opencv/data/haarcascades/haarcascade_eye_tree_eyeglasses.xml')

video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
        #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        frame = cv2.putText(frame, "face", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_8)


        eyes = eyeCascade.detectMultiScale(gray[y:y+h, x:x+w])
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(frame,(ex+x,ey+y),(ex+ew+x,ey+eh+y),(0,255,0),2)
            frame = cv2.putText(frame, "eye", (ex+x, ey+y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1, cv2.LINE_8)



    # frame = cv2.putText(frame, str(datetime.datetime.now()),
    #                     (10, 100),
    #                     cv2.FONT_HERSHEY_SIMPLEX, 1,
    #                     (0, 255, 0),
    #                     4, cv2.LINE_8)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.05)
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
