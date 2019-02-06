import cv2

class Filter(object):
    '''invert colors'''

    def __init__(self, params):
        self.params = params

    def apply(self, img):
        return cv2.bitwise_not(img)
