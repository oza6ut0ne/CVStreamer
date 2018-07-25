import cv2
import numpy as np


class Filter(object):
    '''calc local binary pattern'''

    def __init__(self, params):
        pass

    def apply(self, img, params):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pad = np.pad(gray, [1, 1], 'constant', constant_values=0).astype(np.uint16)

        thresh = (pad[1:-1, 1:-1]
            + pad[:-2, :-2] \
            + pad[1:-1, :-2] \
            + pad[2:, :-2] \
            + pad[2:, 1:-1] \
            + pad[2:, 2:] \
            + pad[1:-1, 2:] \
            + pad[:-2, 2:] \
            + pad[:-2, 1:-1]) / 9 if params[0] == 'm' else pad[1:-1, 1:-1]

        pad[1:-1, 1:-1] = (pad[:-2, :-2] >= thresh) \
            + ((pad[1:-1, :-2] >= thresh) << 1) \
            + ((pad[2:, :-2] >= thresh) << 2) \
            + ((pad[2:, 1:-1] >= thresh) << 3) \
            + ((pad[2:, 2:] >= thresh) << 4) \
            + ((pad[1:-1, 2:] >= thresh) << 5) \
            + ((pad[:-2, 2:] >= thresh) << 6) \
            + ((pad[:-2, 1:-1] >= thresh) << 7)

        if params[0] == 'u':
            U = ((pad[:-2, :-2] >= thresh) ^ (pad[1:-1, :-2] >= thresh)).astype(np.uint8) \
                + ((pad[1:-1, :-2] >= thresh) ^ (pad[2:, :-2] >= thresh)).astype(np.uint8) \
                + ((pad[2:, :-2] >= thresh) ^ (pad[2:, 1:-1] >= thresh)).astype(np.uint8) \
                + ((pad[2:, 1:-1] >= thresh) ^ (pad[2:, 2:] >= thresh)).astype(np.uint8) \
                + ((pad[2:, 2:] >= thresh) ^ (pad[1:-1, 2:] >= thresh)).astype(np.uint8) \
                + ((pad[1:-1, 2:] >= thresh) ^ (pad[:-2, 2:] >= thresh)).astype(np.uint8) \
                + ((pad[:-2, 2:] >= thresh) ^ (pad[:-2, 1:-1] >= thresh)).astype(np.uint8) \
                + ((pad[:-2, 1:-1] >= thresh) ^ (pad[:-2, :-2] >= thresh)).astype(np.uint8)

            pad[1:-1, 1:-1][U>2] = 9

        return cv2.cvtColor(pad[1:-1, 1:-1].astype(np.uint8), cv2.COLOR_GRAY2BGR)
