import cv2

class Filter(object):
    '''apply Canny edge detection'''

    def __init__(self, params):
        try:
            self.thresh1 = float(params[0])
        except (KeyError, ValueError, IndexError):
            self.thresh1 = 50

        try:
            self.thresh2 = float(params[1])
        except (KeyError, ValueError, IndexError):
            self.thresh2 = 110

    def apply(self, img, params):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, self.thresh1, self.thresh2)
        inverse = cv2.bitwise_not(canny)
        return cv2.cvtColor(inverse, cv2.COLOR_GRAY2BGR)
