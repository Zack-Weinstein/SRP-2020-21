# Main file

# Importing required libraries
import os                                   # Library for file management
import shutil                               # Library for file management
import cv2                                  # Library for image manipulation
from numpy.core.records import record       # Library for array management
from picamera import PiCamera               # Library for accessing my camera
from picamera.array import PiRGBArray       # Library for converting camera output to array
import numpy as np                          # Library for array management
import time                                 # Library for time read out

# Declaring global variables
sensitivity = 1.5                   # The percentage change in either direction needed for motion to be detected
evalInterval = 0.25                 # The minimum time between loops
videoBufferLength = 5               # The time in seconds to wait before ending a video recording due to lack of motion
SRes = [1280, 720]                  # The resolution (width, height) of the saved videos and photos
ARes = [256, 144]                   # The resolution (width, height) of the photo captured every loop for analysis
saveDir = '/home/zack/Desktop/'     # The directory in which files are saved
saveType = 'photo'                  # The mode selection between photo and video, this determines weather a video or photo is saved when motion is detected

# Declaring variables before use
chunkData = [0] * 8                                         # A list that contains the current value between 0 and 100 of each of 8 chunks 
lastChunkData = [0] * 8                                     # A list that contains the last value between 0 and 100 of each of 8 chunks
chunkX = ARes[0] / 4                                        # The calculated width of each chunk, this is determined by dividing the horizontal resolution of the photos captured for analysis by 4
chunkY = ARes[1] / 2                                        # The calculated height of each chunk, this is determined by dividing the vertical resolution of the photos captured for analysis by 2
chunkPixs = chunkX * chunkY                                 # The number of pixels in each chunk, calculated by simply multiplying the width and height of each chunk
camera = PiCamera()                                         # Just allows easier refference to the camera
camera.framerate = (30)                                     # Sets the camera frame rate at 30 (frames per second)
camera.rotation = 180                                       # Flips the output of the camera upside down, this just accounts for the orientation of the camera in it's enclosure 
camera.resolution = (SRes[0], SRes[1])                      # Sets the resolution that the camera outputs as the resolution which saved media is in
rawCapture = PiRGBArray(camera, size=(SRes[0], SRes[1]))    # Sets up a stream of data from the camera which simply updates an array with the most recent sesor data every fram
MediaType = [0, 0]                                          # A list which is used to store how many photos or videos have been saved
motionFlag = False                                          # The variable which is set to True when motion is detected
videoSaveEnd = 0                                            # When saving video, this stores the most recent time that motion was detected
recording = False                                           # The variable which stores weather the camera is currently recording video

def newSaveDir():            # A function which finds the next available save directory
    newDir = True                                       # Stores weather a new directory is needed
    global dirNum                                       # Creates a variable as global, in order that it can be refferenced both inside and outside of the function   
    dirNum = 1                                          # Stores the number of the directory found for saving
    while (newDir):                                     # A loop which will run until the variable 'newDir' is set to False
        if os.path.isdir('%s%s' % (saveDir, dirNum)):       # If the directory with the current dirNum exists run the code bellow
            dirNum = dirNum + 1                                 # Add one to the dirNum variable
        else:                                               # If the previous if statement is not satisfied (The directory does not allready exist), run the code bellow
            newDir = False                                      # Record that a new directory is no longer needed
            os.mkdir('%s%s' % (saveDir, dirNum))                # Create the directory with the number not found to allready be a directory

def updateValues():         # A function which updates the buffered values for current camera readout
    global image                                                                            # Sets 'image' to be accesible from inside and outside of the function
    for data in range(0, 8):                                                                # A loop that runs 8 times, from 0 to 7
        chunkData[data] = 0                                                                     # Resets the current chunk value to 0
    im = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)                                            # Converts the image to grayscale                                 
    img = cv2.resize(im, (ARes[0], ARes[1]))                                                # Resizes the image to the analysis resolution
    print()                                                                                 # Prints a blank line, useful for debugging
    for chunkNum in range(0, 8):                                                            # A loop that runs 8 times, from 0 to 7
        print("chunk %s:" % chunkNum, end = " ")                                                # Prints the current loop itteration
        if chunkNum < 4:                                                                        # If the current loop itteration is less than 4 (0, 1, 2, 3)
            Xstart = chunkX * chunkNum                                                              # Sets the horrizontal start value of the current chunk relative to the resolution of the analysis image
            Ystart = chunkY * 0                                                                     # Sets the vertical start value of the current chunk relative to the resolution of the analysis image
        else:                                                                                   # If the current loop iteration is not less than 4 (4, 5, 6, 7)
            Xstart = chunkX * (chunkNum-4)                                                          # Sets the horrizontal start value of the current chunk relative to the resolution of the analysis image
            Ystart = chunkY * 1                                                                     # Sets the vertical start value of the current chunk relative to the resolution of the analysis image
        Xend = Xstart + chunkX                                                                  # Sets the horrizontal end value of the current chunk relative to the resolution of the analysis image
        Yend = Ystart + chunkY                                                                  # Sets the vertical end value of the current chunk relative to the resolution of the analysis image
        for piX in range(int(Xstart), int(Xend)):                                               # Loop through all the collumns of pixels in the current chunk
            for piY in range(int(Ystart), int(Yend)):                                               # Loop through all the pixels in the current collumn
                chunkData[chunkNum] = chunkData[chunkNum] + img[piY, piX]                               # Adds the grayscale value of the current pixel to the data value for the chunk as a whole
        chunkData[chunkNum] = round((chunkData[chunkNum] / chunkPixs) * (100 / 255), 1)         # Converts the result to a number between 0 and 100 from 0 to 255, and rounds it to 1 decimal place
        print(chunkData[chunkNum])                                                              # Prints the resulting value for that chunk (the loop will then begin again at the next number)

def evaluateData():         # A function that evaluates current buffered data in comparison to the last buffered data and determines if there is motion between the two
    global lastChunkData                                                                                    # Allows the list with the previous data for each chunk to be accessed within the function
    for i in range(0, 8):                                                                                   # A loop that runs 8 times, from 0 to 7
        global motionFlag                                                                                       # Allows the 'motionflag' variable to be accessed within the function and loop
        if chunkData[i] > lastChunkData[i] + sensitivity or chunkData[i] < lastChunkData[i] - sensitivity:      # If the change in value of the current chunk is greater than the sensitivity value
            motionFlag = True                                                                                       # The 'motionFlag' variable is set to True
            print("motion in chunk %s" % i)                                                                         # Prints that there was motion detected in the current chunk
        lastChunkData[i] = chunkData[i]                                                                         # Moves the current data to the previous data list

def saveMedia(type):       # A function that saves media when called
    global MediaType                                                                        # Allows 'MediaType' variable to be accessed within the function
    global videoSaveEnd                                                                     # Allows 'videoSaveEnd' variable to be accessed within the function
    global motionFlag                                                                       # Allows 'motionFlag' variable to be accessed within the function
    global recording                                                                        # Allows 'recording' variable to be accessed within the function
    if type == "photo":                                                                     # If the function is called with the condition "photo"
        cv2.imwrite('%s%s/photo_%s.jpg' % (saveDir, dirNum, MediaType[0]), image)               # Saves the photo to the save directory
        MediaType[0] = MediaType[0] + 1                                                         # Adds one to the variable that stores the number of photo saves
        print("save %s" % MediaType[0])                                                         # Prints the current save number
    if type == "video":                                                                     # If the function is called with the condition "video"
        nowTime = time.time()                                                                   # Saves the current time to a variable, this is done because retrieving the time is a very time consuming process
        if recording and motionFlag:                                                            # If a video is allready being recorded, and motion is detected
            videoSaveEnd = nowTime                                                                  # Sets 'videoSaveEnd' Variable to current time
        elif videoSaveEnd + videoBufferLength <= nowTime and recording:                         # Else, if the last time motion was detected + the buffer length is less than the current time, and it is allready recording video
            camera.stop_recording()                                                                 # Stop recording
            recording = False                                                                       # Sets recording flag to False
            MediaType[1] = MediaType[1] + 1                                                         # Adds one to the variable that stores how many video saves have occured
        elif recording:                                                                         # Else, if it is allready recording video
            pass                                                                                    # Do nothing
        elif motionFlag:                                                                        # Else, if motion is detected
            saveMedia('photo')                                                                      # Save the photo with motion detected in it
            camera.start_recording('%s%s/video_%s.h264' % (saveDir, dirNum, MediaType[1]))          # Start a new video recording
            recording = True                                                                        # Set the recording flag to True
            videoSaveEnd = nowTime                                                                  # Set the last motion time during recording to the current time
        print("save %s" % MediaType[1])                                                             # Print the save number

def resetCache():           # Function that resets openCV stream
    rawCapture.truncate(0)  # Resets the stream of data

try:    # Attempt to run the following code, if it fails, move to the except statement; note, this is the only place code is actually run, all previous code i just setting up functions, variable, etc, to run in this chunk
    resetCache()                                                                            # Runs the resetCache() function
    newSaveDir()                                                                            # Runs the newSaveDir() function
    lastEvalTime = 0                                                                        # Sets the 'lastEvalTime' variable to 0
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):  # Loop infinitely through the most recent frame of the camera
        loop = True                                                                             # Sets the 'loop' variable to True
        while loop:                                                                             # Loop as long as the 'loop' variable is True
            currentInterval = round(time.time() - lastEvalTime, 2)                                  # Sets the current interval to the current time - the last evaluation time, and rounds it to 1 decimal place
            if currentInterval >= evalInterval:                                                     # If the current interval is greater than the use set eval interval
                loop = False                                                                            # Set the loop variable to be false
                lastEvalTime = round(time.time(), 2)                                                    # Records the current time rounded to 2 decimal places to the 'lastEvalTime' variable
                image = frame.array                                                                     # Captures an image as an array to the 'image' variable
                updateValues()                                                                          # Runs the updateValues() function
                evaluateData()                                                                          # Runs the evauateData() function
                if motionFlag or recording:                                                             # If there is motion or it is allready recording
                    saveMedia(saveType)                                                                     # Runs the saveMedia() function
                motionFlag = False                                                                      # Sets the 'motionFlag' variable to False
                print("Loop Start: %s" % lastEvalTime)                                                  # Prints the time at which the loop started
                print("Loop Time:  %s" % currentInterval)                                               # Prints how long the loop took
        resetCache()                                                                            # Runs the resetCache() function
except: # If the code within the try statement fails, run this
    print("\n\n  ** Program End Via Keyboard Interupt **  \n")      # Prints an error message