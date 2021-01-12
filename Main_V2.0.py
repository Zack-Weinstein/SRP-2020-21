# Main file

import os
import shutil
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
from multiprocessing import Process
import time

h = 1

sensitivity = 1.5
evalInterval = 0.2
motionFlag = False
chunks = ["aa", "ab", "ac", "ad", "ba", "bb", "bc", "bd",]
chunkData = [0, 0, 0, 0, 0, 0, 0, 0]
lastChunkData = [0, 0, 0, 0, 0, 0, 0, 0]
resX = 896
resY = 504
aResX = 256
aResY = 144
chunkX = aResX / 4
chunkY = aResY / 2
chunkPixs = chunkX * chunkY
camera = PiCamera()
camera.resolution = (resX, resY)
camera.framerate = (30)
ph = 0
vi = 0
newDir = True
dirNum = 1
rawCapture = PiRGBArray(camera, size=(resX, resY))
while (newDir):
    if os.path.isdir('/home/pi/Desktop/%s' % dirNum):
        dirNum = dirNum + 1
    else:
        newDir = False
        os.mkdir('/home/pi/Desktop/%s' % dirNum)

def capture(type, length):
    camera.resolution = (resX, resY)
    if type == "photo":
        camera.capture('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph)
    if type == "video":
        camera.start_recording('/home/pi/Desktop/Analysis/video_%s.h264' % vi)
        sleep(length)
        camera.stop_recording()

def updateValues():
    global image
    for data in range(0, 8):
        chunkData[data] = 0
    #camera.resolution = (resX, resY)
    #camera.capture('/home/pi/Desktop/Analysis/photo.jpg')
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(im, (aResX, aResY))
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

def evaluateData():
    global lastChunkData
    for i in range(0, 8):
        global motionFlag
        if chunkData[i] > lastChunkData[i] + sensitivity or chunkData[i] < lastChunkData[i] - sensitivity:
            motionFlag = True
            print("motion in chunk %s" % i)
        lastChunkData[i] = chunkData[i]

def saveMedia(type):
    global ph
    global vi
    if type == "photo":
        #shutil.move('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph, '/home/pi/Desktop/%s' % dirNum)
        cv2.imwrite('/home/pi/Desktop/%s/photo_%s.jpg' % (dirNum, ph), image)
        ph = ph + 1
    if type == "video":
        shutil.move('/home/pi/Desktop/Analysis/video_%s.h264' % vi, '/home/pi/Desktop/%s' % dirNum)
        vi = vi + 1
    print("save %s" % ph)

def resetCache():
    #shutil.rmtree('/home/pi/Desktop/Analysis')
    #os.mkdir('/home/pi/Desktop/Analysis')
    rawCapture.truncate(0)

if __name__ == "__main__":
    resetCache()
    lastEvalTime = 0
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):   
        if time.time() > lastEvalTime + evalInterval:
            lastEvalTime = time.time()
            image = frame.array
            updateValues()
            evaluateData()
            if motionFlag:
                saveMedia("photo")
            motionFlag = False
            print(lastEvalTime)
        resetCache()