import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera 
import numpy as np 

sensitivity = 3
motionFlag = False
chunks = ["aa", "ab", "ac", "ad", "ba", "bb", "bc", "bd",]
chunkData = [0, 0, 0, 0, 0, 0, 0, 0]
lastChunkData = [0, 0, 0, 0, 0, 0, 0, 0]
resX = 640
resY = 480
chunkX = resX / 4
chunkY = resY / 2
chunkPixs = chunkX * chunkY
camera = PiCamera()
camera.resolution = (resX, resY)
camera.framerate = (30)
rawCapture = PiRGBArray(camera, size=(640, 480))
recent = True

def updateValues():
    for data in range(0, 8):
        chunkData[data] = 0
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	    img = frame.array
        if recent == True:
            break
    print()
    for chunkNum in range(0, 8):
        print("chunk %s" % chunkNum)
        if chunkNum < 4:
            Xstart = chunkX * chunkNum
            Ystart = chunkY * 0
        else:
            Xstart = chunkX * (chunkNum-4)
            Ystart = chunkY * 1 
        Xend = Xstart + chunkX
        Yend = Ystart + chunkY
        for piX in range(int(Xstart), int(Xend)):
            for piY in range(int(Ystart), int(Yend)):
                chunkData[chunkNum] = chunkData[chunkNum] + img[piY, piX]
        chunkData[chunkNum] = round((chunkData[chunkNum] / chunkPixs) * (100 / 255))
        print(chunkData[chunkNum])

updateValues()