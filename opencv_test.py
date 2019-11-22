try:
    from cv2 import cv2
except ImportError:
    pass
import json


center_list = []


def get_center(frame, low, high, draw):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, low, high)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cv2.imshow("Mask", mask)

    if len(contours) == 0:
        return frame, []

    valid_contour = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 2500 < area:
            print(area)
            cv2.drawContours(frame, [contour], 0, (255, 0, 0), 3)

            epsilon = 0.025 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if draw:
                cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)

            M = cv2.moments(approx)
            if M["m00"] == 0:
                return frame, (-1, -1)

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            if draw:
                cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)

            valid_contour.append((contour, area, (cx, cy)))

    return frame, valid_contour

    # contour_max = contours[0]
    # for contour in contours:
    #     area = cv2.contourArea(contour)
    #     area_max = cv2.contourArea(contour_max)
    #     if area > area_max:
    #         contour_max = contour
    #
    # if cv2.contourArea(contour_max) < 2500:
    #     return frame, (-1, -1)

    # cv2.drawContours(frame, [contour_max], 0, (255, 0, 0), 3)
    # epsilon = 0.025 * cv2.arcLength(contour_max, True)
    # approx = cv2.approxPolyDP(contour_max, epsilon, True)
    # if draw:
    #     cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)
    #
    # M = cv2.moments(approx)
    # if M["m00"] == 0:
    #     return frame, (-1, -1)
    #
    # cx = int(M["m10"] / M["m00"])
    # cy = int(M["m01"] / M["m00"])
    # if draw:
    #     cv2.circle(frame, (cx, cy), 7, (255, 0, 0), -1)
    #
    # return frame, (cx, cy)


def main(target):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Get Maximum Resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100000)

    max_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    max_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print("Max Resolution : {0}x{1}".format(max_width, max_height))

    # low, high = setRange()
    low = (35, 75, 50)
    high = (80, 150, 255)

    while True:
        ret, frame = cap.read()
        if frame is None:
            print("Received Frame None")
            break

        frame = cv2.resize(frame, target)
        frame_hint, center = get_center(frame, low, high, True)
        # if len(center) > 0:
        #     center_list.append({"x": center[0], "y": center[1]})

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) > 0:
            f = open("log.json", "w")
            f.write(json.dumps(center_list))
            f.close()
            break


if __name__ == "__main__":
    main((1280, 720))
