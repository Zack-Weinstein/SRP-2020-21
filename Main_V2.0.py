# Main file

# Importing required libraries
import os
import shutil
import cv2
from numpy.core.records import record
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import time

# Declaring global variables
sensitivity = 1.5
evalInterval = 0.2
videoBufferLength = 5
SRes = [1280, 720]
ARes = [256, 144]
saveDir = '/home/pi/Desktop/'
saveType = 'video'

# Declaring variables before use
chunkData = [0] * 8
lastChunkData = [0] * 8
chunkX = ARes[0] / 4
chunkY = ARes[1] / 2
chunkPixs = chunkX * chunkY
#videoStop = videoBufferLength / evalInterval
camera = PiCamera()
camera.framerate = (30)
camera.rotation = 180
camera.resolution = (SRes[0], SRes[1])
rawCapture = PiRGBArray(camera, size=(SRes[0], SRes[1]))
MediaType = [0, 0]
motionFlag = False
videoSaveEnd = 0
recording = False

def newSaveDir():            # Finds next available save directory
    newDir = True
    global dirNum
    dirNum = 1
    while (newDir):
        if os.path.isdir('%s%s' % (saveDir, dirNum)):
            dirNum = dirNum + 1
        else:
            newDir = False
            os.mkdir('%s%s' % (saveDir, dirNum))

def updateValues():         # Updates buffered values for current camera readout
    global image
    for data in range(0, 8):
        chunkData[data] = 0
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(im, (ARes[0], ARes[1]))
    print()
    for chunkNum in range(0, 8):
        print("chunk %s:" % chunkNum, end = " ")
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
        chunkData[chunkNum] = round((chunkData[chunkNum] / chunkPixs) * (100 / 255), 1)
        print(chunkData[chunkNum])

def evaluateData():         # Evaluates current buffered data in comparison to the last buffered data and determines if there is motion between the two.
    global lastChunkData
    for i in range(0, 8):
        global motionFlag
        if chunkData[i] > lastChunkData[i] + sensitivity or chunkData[i] < lastChunkData[i] - sensitivity:
            motionFlag = True
            print("motion in chunk %s" % i)
        lastChunkData[i] = chunkData[i]

def saveMedia(type):       # Saves media stored in openCV numpy array
    global MediaType
    global videoSaveEnd
    global motionFlag
    global videoStop
    global recording
    if type == "photo":
        cv2.imwrite('%s%s/photo_%s.jpg' % (saveDir, dirNum, MediaType[0]), image)
        MediaType[0] = MediaType[0] + 1
        print("save %s" % MediaType[0])
    if type == "video":
        nowTime = time.time()
        if recording and motionFlag:
            videoSaveEnd = nowTime
        elif (videoSaveEnd + videoBufferLength <= nowTime) and recording == False:
            camera.stop_recording()
            recording = False
            MediaType[1] = MediaType[1] + 1
            videoSaveEnd = nowTime
        elif recording:
            pass
        elif motionFlag:
            camera.start_recording('%s%s/video_%s.h264' % (saveDir, dirNum, MediaType[1]))
            recording = True
        print("save %s" % MediaType[1])

def resetCache():           # Resets openCV stream
    rawCapture.truncate(0)

#try:
resetCache()
newSaveDir()
lastEvalTime = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    currentInterval = round(time.time() - lastEvalTime, 2)
    if currentInterval >= evalInterval:
        lastEvalTime = round(time.time(), 2)
        image = frame.array
        updateValues()
        evaluateData()
        if motionFlag or recording:
            saveMedia(saveType)
        motionFlag = False
        print("Loop Start: %s" % lastEvalTime)
        print("Loop Time:  %s" % currentInterval)
    resetCache()
#except:
#    print("\n")
#    print("  ** Program End Via Keyboard Interupt **  ")