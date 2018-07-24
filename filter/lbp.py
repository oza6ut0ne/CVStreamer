import cv2
import numpy as np


class Filter(object):
    '''calc local binary pattern'''

    def __init__(self, params):
        pass

    def apply(self, img, params):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pad = np.pad(gray, [1, 1], 'constant', constant_values=0)

        pad[1:-1, 1:-1] = (pad[:-2, :-2] < pad[1:-1, 1:-1]) \
            + ((pad[1:-1, :-2] < pad[1:-1, 1:-1]) << 1) \
            + ((pad[2:, :-2] < pad[1:-1, 1:-1]) << 2) \
            + ((pad[2:, 1:-1] < pad[1:-1, 1:-1]) << 3) \
            + ((pad[2:, 2:] < pad[1:-1, 1:-1]) << 4) \
            + ((pad[1:-1, 2:] < pad[1:-1, 1:-1]) << 5) \
            + ((pad[:-2, 2:] < pad[1:-1, 1:-1]) << 6) \
            + ((pad[:-2, 1:-1] < pad[1:-1, 1:-1]) << 7)

        return cv2.cvtColor(pad[1:-1, 1:-1], cv2.COLOR_GRAY2BGR)
