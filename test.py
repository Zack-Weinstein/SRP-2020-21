from picamera import PiCamera
camera = PiCamera()
camera.resolution = (1920, 1080)
ph = 0

while(True):
    camera.capture('/home/pi/Desktop/photo_%s.png' % ph)
    ph = ph + 1