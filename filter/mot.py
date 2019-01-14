import cv2
import numpy as np
import time

class Filter(object):
    '''detects motions with cv2.BackgroundSubtractorMOG2'''

    def __init__(self, params):
        try:
            varThreshold = float(params[0])
            if varThreshold <= 0:
                varThreshold = 16
        except (KeyError, ValueError, IndexError):
                varThreshold = 16
        try:
            self.learningRate = float(params[1])
            if self.learningRate <= 0:
                self.learningRate = 0.01
        except (KeyError, ValueError, IndexError):
                self.learningRate = 0.01

        self.bsub = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=varThreshold)

    def apply(self, img):
        height, width, _ = img.shape
        tile = np.tile(np.uint8(np.asarray([0, 0, 255])), (height, width, 1))
        mask = self.bsub.apply(img, learningRate=self.learningRate)

        if (int(time.time() * 1000) % 400) < 200:
            filter = cv2.bitwise_and(tile, tile, mask=mask)
            result = cv2.bitwise_or(img, filter)
        else:
            result = img

        return result
