import cv2

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
ph = 0
vi = 0


def updateValues(color):
    for data in range(0, 8):
        chunkData[data] = 0
    img = cv2.imread('/home/pi/Desktop/%s.jpg' % color, cv2.IMREAD_GRAYSCALE)
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

updateValues("white")
updateValues("black")