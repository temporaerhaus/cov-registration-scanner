import cv2
import print2
import time

webcam = cv2.VideoCapture(0)
qrDecoder = cv2.QRCodeDetector()

while(true):
    (_, im) = webcam.read()
    (data, _, _) = qrDecoder.detectAndDecode(im)
    if(data!=''):
        print2.printR(data)
        time.sleep(5)