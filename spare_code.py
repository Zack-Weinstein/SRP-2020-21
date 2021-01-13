shutil.rmtree('/home/pi/Desktop/Analysis')
os.mkdir('/home/pi/Desktop/Analysis')
camera.resolution = (resX, resY)
camera.capture('/home/pi/Desktop/Analysis/photo.jpg')
shutil.move('/home/pi/Desktop/Analysis/photo_%s.jpg' % MediaType[0], '/home/pi/Desktop/%s' % dirNum)
camera.resolution = (resX, resY)
camera.capture('/home/pi/Desktop/Analysis/photo.jpg')

if type == "video":
        shutil.move('/home/pi/Desktop/Analysis/video_%s.h264' % MediaType[1], '/home/pi/Desktop/%s' % dirNum)
        MediaType[1] = MediaType[1] + 1

def capture(type, length):  # Captures specified type of media
    camera.resolution = (SRes[0], SRes[1])
    if type == "photo":
        camera.capture('/home/pi/Desktop/Analysis/photo_%s.jpg' % MediaType[0])
    if type == "video":
        camera.start_recording('/home/pi/Desktop/Analysis/video_%s.h264' % MediaType[1])
        sleep(length)
        camera.stop_recording()