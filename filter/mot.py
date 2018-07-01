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
        self.bsub = cv2.createBackgroundSubtractorMOG2(detectShadows=False, varThreshold=varThreshold)

    def apply(self, img, params):
        height, width, _ = img.shape
        tile = np.tile(np.uint8(np.asarray([0, 0, 255])), (height, width, 1))
        try:
            learningRate = float(params[1])
            if learningRate <= 0:
                learningRate = 0.01
        except (KeyError, ValueError, IndexError):
                learningRate = 0.01
        mask = self.bsub.apply(img, learningRate=learningRate)

        if (int(time.time() * 1000) % 400) < 200:
            filter = cv2.bitwise_and(tile, tile, mask=mask)
            result = cv2.bitwise_or(img, filter)
        else:
            result = img

        return result
