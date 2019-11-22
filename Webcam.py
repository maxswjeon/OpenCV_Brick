from threading import Thread
from filterpy.kalman import UnscentedKalmanFilter

import cv2
try:
    from cv2 import cv2
except ImportError:
    pass


class Webcam(Thread):
    def __init__(self, capture: cv2.VideoCapture, low: tuple, high: tuple):
        self.capture = capture
        self.running = True
        self.frame = None
        self.onFrameRead = []
        self.low = low
        self.high = high
        self.left = (-1, -1)
        self.right = (-1, -1)
        self.center = -1
        super().__init__()

    def get_center(self, frame):
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.low, self.high)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return frame, []

        valid_contour = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 800:
                continue
            epsilon = 0.025 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            M = cv2.moments(approx)
            if M["m00"] == 0:
                return frame, (-1, -1)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            valid_contour.append((contour, area, (cx, cy)))

        return frame, valid_contour

    def run(self):
        while self.running:
            ret, frame = self.capture.read()

            for cb in self.onFrameRead:
                append, frame_mod = cb(frame.copy())
                if append:
                    frame = frame_mod

            _, self.balls = self.get_center(frame)
            if len(self.balls) == 2:
                self.center = (self.balls[0][2][0] + self.balls[1][2][0]) / 2

            self.frame = frame

    def stop(self):
        self.running = False

    def get_frame(self):
        return self.frame
