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

        self.lut = np.arange(0, 256).reshape(256, 1)
        self.lut[self.lut < self.thresh] = 0
        self.lut[self.lut != 0] -= self.thresh
        self.lut *= 255
        self.lut //= (255 - self.thresh)
        self.lut = self.lut.astype(np.uint8)

    def shadow(self, img):
        return  cv2.LUT(img, self.lut)

    def screen(self, img1, img2):
        inv1 = cv2.bitwise_not(img1)
        inv2 = cv2.bitwise_not(img2)
        mul = inv1 / 255 * inv2
        mul = mul.astype(np.uint8)
        return cv2.bitwise_not(mul)

    def apply(self, img):
        copy = self.shadow(img)
        copy = cv2.GaussianBlur(copy, (0, 0), self.rad)
        return self.screen(copy, img)
