import cv2
import numpy as np

class Filter(object):
    '''apply gamma collection'''

    def __init__(self, params):
        try:
            self.gamma = float(params[0])
            if self.gamma == 0:
                self.gamma = 0.1
        except (KeyError, ValueError, IndexError):
            self.gamma = 2.0

    def apply(self, img, params):
        lookup_table = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            lookup_table[i][0] = 255 * pow(float(i)/255, 1.0/self.gamma)
        return  cv2.LUT(img, lookup_table)                          
