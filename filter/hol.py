import itertools
import time

import cv2
import numpy as np


class Filter(object):
    '''add hologram effect
    inspired by https://elder.dev/posts/open-source-virtual-background/
    '''

    def __init__(self, params):
        self.params = params
        try:
            self.band_scale = int(params[0])
        except (KeyError, ValueError, IndexError):
            self.band_scale = 1
        try:
            self.velocity = int(params[1])
        except (KeyError, ValueError, IndexError):
            self.velocity = -1

        self.band_dark = 2 * self.band_scale
        self.band_bright = 3 * self.band_scale
        self.band_length = self.band_dark + self.band_bright
        self.cycle_counter = itertools.cycle(range(self.band_length))

    def shift_image(self, img, dx, dy):
        img = np.roll(img, dy, axis=0)
        img = np.roll(img, dx, axis=1)
        if dy > 0:
            img[:dy, :] = 0
        elif dy < 0:
            img[dy:, :] = 0
        if dx > 0:
            img[:, :dx] = 0
        elif dx < 0:
            img[:, dx:] = 0
        return img

    def apply(self, img):
        holo = cv2.applyColorMap(img, cv2.COLORMAP_WINTER)
        if self.velocity == -1:
            offset_y = next(self.cycle_counter)
        else:
            offset_y = int(time.time() * self.velocity) % self.band_length
        for y in range(holo.shape[0] - offset_y):
            if y % self.band_length < self.band_dark:
                holo[y + offset_y] = holo[y + offset_y] * np.random.uniform(0.1, 0.3)

        holo_blur = cv2.addWeighted(holo, 0.2, self.shift_image(holo.copy(), 5, 5), 0.8, 0)
        holo_blur = cv2.addWeighted(holo_blur, 0.4, self.shift_image(holo.copy(), -5, -5), 0.6, 0)

        result = cv2.addWeighted(img, 0.5, holo_blur, 0.6, 0)
        return result
