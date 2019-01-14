import cv2
import numpy as np

class Filter(object):
    '''apply dilate diff edge detection'''

    def __init__(self, params):
        self.nb8 = np.array([[1,1,1],[1,1,1],[1,1,1]],np.uint8)

    def apply(self, img):
        dilate = cv2.dilate(img, self.nb8, iterations=2)
        diff = cv2.absdiff(img, dilate)
        res = cv2.bitwise_not(diff)
        return res
