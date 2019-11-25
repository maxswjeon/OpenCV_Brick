import cProfile
from threading import Thread

import cv2

try:
    from cv2 import cv2
except ImportError:
    pass


class Webcam(Thread):
    def __init__(self, capture: cv2.VideoCapture, frame_size: tuple, padding: tuple, low: tuple, high: tuple,
                 roi: tuple):
        self.capture = capture
        self.running = True
        self.frame = None
        self.frame_size = frame_size
        self.padding = padding
        self.onFrameRead = []
        self.low = low
        self.high = high
        self.left = (-1, -1)
        self.right = (-1, -1)
        self.center = -1
        self.roi = roi
        self.last_update = 0
        self.updated = False
        self.pr = cProfile.Profile()
        super().__init__()

    def get_center(self, frame):
        self.pr.enable()
        if self.roi[0] != -1 and self.roi[1] != -1:
            frame = frame[self.roi[0]:self.roi[1], 0:frame.shape[1]]

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

        self.pr.disable()
        return frame, valid_contour

    def resize_ratio(self, frame):
        # Check Ratio
        ratio_req = self.frame_size[0] / self.frame_size[1]
        ratio_org = frame.shape[1] / frame.shape[0]
        if ratio_org == ratio_req:
            return cv2.resize(frame, self.frame_size)

        size_bwidth = (
            self.frame_size[0],
            int(self.frame_size[0] / frame.shape[1] * frame.shape[0])
        )

        if size_bwidth[1] > self.frame_size[1]:
            start = int((size_bwidth[1] - self.frame_size[1]) / 2)
            frame = cv2.resize(frame, size_bwidth)
            frame = frame[start:start + self.frame_size[1], 0:self.frame_size[0]]
            return frame

        size_bheight = (
            int(self.frame_size[1] / frame.shape[0] * frame.shape[1]),
            self.frame_size[1]
        )

        start = int((size_bheight[0] - self.frame_size[0]) / 2)
        frame = cv2.resize(frame, size_bheight)
        frame = frame[0:self.frame_size[1], start:start + self.frame_size[0]]
        return frame

    def run(self):
        while self.running:
            self.pr.enable()
            ret, frame = self.capture.read()

            # if self.last_update == 0:
            #     self.last_update = time.time()
            # else:
            #     print(1 / (time.time() - self.last_update))
            #     self.last_update = time.time()

            frame = self.resize_ratio(frame)
            frame = frame[self.padding[0]:-self.padding[2], self.padding[3]:-self.padding[1]]

            _, self.balls = self.get_center(frame)
            if len(self.balls) == 2:
                self.center = (self.balls[0][2][0] + self.balls[1][2][0]) / 2

            self.frame = frame
            self.updated = True
            self.pr.disable()

    def stop(self):
        self.running = False

    def get_frame(self):
        self.updated = False
        return self.frame

    def is_updated(self):
        return self.updated
