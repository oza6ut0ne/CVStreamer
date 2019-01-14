import cv2

class Filter(object):
    '''invert colors'''

    def __init__(self, params):
        pass

    def apply(self, img):
        return cv2.bitwise_not(img)
