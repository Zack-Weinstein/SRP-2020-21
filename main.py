# Main file

import os
import shutil
import cv2
from picamera import PiCamera
from time import sleep

sensitivity = 0.1
motionFlag = False
chunks = ["aa", "ab", "ac", "ad", "ba", "bb", "bc", "bd",]
chunkData = [0, 0, 0, 0, 0, 0, 0, 0]
lastChunkData = [0, 0, 0, 0, 0, 0, 0, 0]
resX = 1920
resY = 1080
chunkX = resX / 4
chunkY = resY / 2
chunkPixs = chunkX * chunkY
camera = PiCamera()
camera.resolution = (resX, resY)
camera.framerate = (30)
ph = 0
vi = 0
newDir = True
dirNum = 1
while (newDir):
    if os.path.isdir('/home/pi/Desktop/%s' % dirNum):
        dirNum = dirNum + 1
    else:
        newDir = False
        os.mkdir('/home/pi/Desktop/%s' % dirNum)

def capture(type, length):
    if type == "photo":
        camera.capture('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph)
    if type == "video":
        camera.start_recording('/home/pi/Desktop/Analysis/video_%s.h264' % vi)
        sleep(length)
        camera.stop_recording()

def updateValues():
    for data in range(0, 8):
        chunkData[data] = 0
    img = cv2.imread('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph, cv2.IMREAD_GRAYSCALE)
    for chunkNum in range(0, 8):
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

def evaluateData():
    for i in range(0, 8):
        if chunkData[i] > (lastChunkData[i] + (sensitivity * lastChunkData[i])) or chunkData[i] < (lastChunkData[i] - (sensitivity * lastChunkData[i])):
            return True
        lastChunkData[i] = chunkData[i]

def saveMedia(type):
    if type == "photo":
        global ph
        shutil.move('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph, '/home/pi/Desktop/%s' % dirNum)
        ph = ph + 1
    if type == "video":
        shutil.move('/home/pi/Desktop/Analysis/video_%s.h264' % vi, '/home/pi/Desktop/%s' % dirNum)
        vi = vi + 1

def resetCache():
    shutil.rmtree('/home/pi/Desktop/Analysis')
    os.mkdir('/home/pi/Desktop/Analysis')

resetCache()
while(True):
    capture("photo", 1)
    updateValues()
    if evaluateData():
        saveMedia("photo")
    else:
        resetCache()
    sleep(0.2)