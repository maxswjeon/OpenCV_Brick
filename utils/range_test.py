try:
    from cv2 import cv2
except ImportError:
    pass


def get_mask(frame, low, high, mask_type=None):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    mask_h = cv2.inRange(h, low[0], high[0])
    mask_h = cv2.morphologyEx(mask_h, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_s = cv2.inRange(s, low[0], high[0])
    mask_s = cv2.morphologyEx(mask_s, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_v = cv2.inRange(v, low[0], high[0])
    mask_v = cv2.morphologyEx(mask_v, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_hh = cv2.inRange(h, high[0], 255)
    mask_hh = cv2.morphologyEx(mask_hh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_hl = cv2.inRange(h, 0, low[0])
    mask_hl = cv2.morphologyEx(mask_hl, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_sh = cv2.inRange(s, high[1], 255)
    mask_sh = cv2.morphologyEx(mask_sh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_sl = cv2.inRange(s, 0, low[1])
    mask_sl = cv2.morphologyEx(mask_sl, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_vh = cv2.inRange(v, high[2], 255)
    mask_vh = cv2.morphologyEx(mask_vh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    mask_vl = cv2.inRange(v, 0, low[2])
    mask_vl = cv2.morphologyEx(mask_vl, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    masks = [
        mask_h,
        mask_s,
        mask_v,
        mask_hh,
        mask_hl,
        mask_sh,
        mask_sl,
        mask_vh,
        mask_vl
    ]
    mask = masks[mask_type]
    mask = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow("Mask", mask)


def view_center(frame, low, high):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 800:
            continue
        cv2.drawContours(frame, [contour], 0, (0, 255, 0), 3)

        epsilon = 0.025 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        M = cv2.moments(approx)
        if M["m00"] == 0:
            return frame, (-1, -1)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.drawContours(frame, [contour], 0, (255, 0, 0), 3)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    cv2.imshow("Capture", frame)
    cv2.imshow("Mask", mask)


def main(target):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Get Maximum Resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100000)

    max_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    max_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print("Max Resolution : {0}x{1}".format(max_width, max_height))

    # low, high = setRange()
    low = [90, 139, 81]
    high = [187, 255, 176]

    mask_type = 3

    while True:
        ret, frame = cap.read()
        if frame is None:
            print("Received Frame None")
            break

        frame = cv2.flip(frame, 1)

        if mask_type < 9:
            get_mask(frame, tuple(low), tuple(high), mask_type)
        elif mask_type == 9:
            view_center(frame, tuple(low), tuple(high))
        else:
            break

        key = cv2.waitKey(1)

        i = int((mask_type - 3) / 2)
        if key == 13:
            mask_type += 1
        elif key == 43:
            if mask_type % 2:
                high[i] += 10
            else:
                low[i] += 10
            print(high)
            print(low)
            print()
        elif key == 45:
            if mask_type % 2:
                high[i] -= 10
            else:
                low[i] -= 10
            print(high)
            print(low)
            print()
        elif key == ord('r'):
            mask_type = 3


if __name__ == "__main__":
    main((1280, 720))
