import time

import cv2
import numpy as np

class Filter(object):
    '''detects motions with cv2.BackgroundSubtractorMOG2'''

    def __init__(self, params):
        self.params = params
        try:
            varThreshold = float(params[0])
            if varThreshold <= 0:
                varThreshold = 16
        except (KeyError, ValueError, IndexError):
                varThreshold = 16
        try:
            self.learningRate = float(params[1])
        except (KeyError, ValueError, IndexError):
            self.learningRate = 0.01

        self.subtor = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=varThreshold)

    def apply(self, img):
        mask = self.subtor.apply(img, learningRate=self.learningRate)
        if (int(time.time() * 1000) % 400) < 200:
            img[:, :, 2] |= mask

        return img
