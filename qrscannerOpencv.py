import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
#import print2
import time
import vobject

webcam = cv2.VideoCapture(0)

while(True):
    (_, im) = webcam.read()
    decodedObjects = pyzbar.decode(im)
    for obj in decodedObjects:
      #print(obj.data.decode('utf-8'), "\n")
      v = vobject.readOne  ( obj.data.decode('utf-8') )
      print(v.n.value)
      print(v.email.value)
      print(v.tel.value)
      for adr in v.contents['adr']:
         print(adr.value)
