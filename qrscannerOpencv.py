import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import print2
import time

webcam = cv2.VideoCapture(0)

while(True):
    (_, im) = webcam.read()
    decodedObjects = pyzbar.decode(im)
    for obj in decodedObjects:
      print(obj.data, "\n")
