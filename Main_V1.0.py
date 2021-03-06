# Main file

import os
import shutil
import cv2
from picamera import PiCamera
from time import sleep

sensitivity = 3
motionFlag = False
chunks = ["aa", "ab", "ac", "ad", "ba", "bb", "bc", "bd",]
chunkData = [0, 0, 0, 0, 0, 0, 0, 0]
lastChunkData = [0, 0, 0, 0, 0, 0, 0, 0]
resX = 1920
resY = 1080
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
    for data in range(0, 8):
        chunkData[data] = 0
    camera.resolution = (aResX, aResY)
    camera.capture('/home/pi/Desktop/Analysis/photo.jpg')
    img = cv2.imread('/home/pi/Desktop/Analysis/photo.jpg', cv2.IMREAD_GRAYSCALE)
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
        shutil.move('/home/pi/Desktop/Analysis/photo_%s.jpg' % ph, '/home/pi/Desktop/%s' % dirNum)
        ph = ph + 1
    if type == "video":
        shutil.move('/home/pi/Desktop/Analysis/video_%s.h264' % vi, '/home/pi/Desktop/%s' % dirNum)
        vi = vi + 1
    print("save %s" % ph)

def resetCache():
    shutil.rmtree('/home/pi/Desktop/Analysis')
    os.mkdir('/home/pi/Desktop/Analysis')

resetCache()
while(True):
    capture("photo", 1)
    updateValues()
    evaluateData()
    if motionFlag:
        saveMedia("photo")
    resetCache()
    motionFlag = False
    #sleep(0.2)