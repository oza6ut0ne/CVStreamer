import cv2
import numpy as np

class Filter(object):
    '''apply gamma collection'''

    def __init__(self, params):
        pass

    def apply(self, img, params):
        try:
            gamma = float(params[0])
            if gamma == 0:
                gamma = 0.1
        except (KeyError, ValueError, IndexError):
            gamma = 2.0

        lookup_table = np.zeros((256, 1), dtype=np.uint8)
        for i in range(256):
            lookup_table[i][0] = 255 * pow(float(i)/255, 1.0/gamma)
        return  cv2.LUT(img, lookup_table)                          
