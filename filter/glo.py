import cv2
import numpy as np

class Filter(object):
    '''apply glow effect'''

    def __init__(self, params):
        try:
            self.thresh = int(params[0])
            if self.thresh < 0:
                self.thresh = 0
        except (KeyError, ValueError, IndexError):
            self.thresh = 128

        try:
            self.rad = float(params[1])
            if self.rad <= 0:
                self.rad = 0.01
        except (KeyError, ValueError, IndexError):
            self.rad = 4.7

    def shadow(self, img, threshold):
        copy = img.astype(np.float)
        copy[copy < threshold] = 0
        copy[copy != 0] -= threshold
        copy *= 255.
        copy /= (255. - threshold)
        return copy.astype(np.uint8)

    def screen(self, img1, img2):
        inv1 = cv2.bitwise_not(img1)
        inv2 = cv2.bitwise_not(img2)
        mul = 255. * (inv1 / 255.) * (inv2 / 255.)
        mul = mul.astype(np.uint8)
        return cv2.bitwise_not(mul)

    def apply(self, img, params):
        copy = self.shadow(img, self.thresh)
        copy = cv2.GaussianBlur(copy, (0, 0), self.rad)
        return self.screen(copy, img)
