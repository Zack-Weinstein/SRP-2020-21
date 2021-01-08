from picamera import PiCamera
camera = PiCamera()
camera.resolution = (256, 144)
ph = 0

while(True):
    camera.capture('/home/pi/Desktop/photo_%s.jpg' % ph)
    ph = ph + 1