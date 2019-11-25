try:
    from cv2 import cv2
except ImportError:
    pass
import matplotlib.pyplot as plt
import numpy as np


def calculate(frame_raw, pos, radius, limit):
    frame = frame_raw.copy()

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    frame = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)

    cv2.circle(mask, pos, radius, (255, 255, 255), -1)
    frame = cv2.bitwise_and(frame, frame, mask=mask)

    frame = frame[pos[1] - radius:pos[1] + radius, pos[0] - radius:pos[0] + radius]

    hsv = np.zeros((3, 256), dtype=np.uint8)

    count = 0
    for y in range(frame.shape[0]):
        for x in range(frame.shape[1]):
            if np.all(frame[y][x] == 0):
                continue
            for i in range(3):
                hsv[i][frame[y][x][i]] += 1
            count += 1

    print('Valid Pixel Count : {0}'.format(count))
    print('limit : {0}'.format(limit))

    min_l_hsv = [-1, -1, -1]
    max_l_hsv = [-1, -1, -1]

    min_hsv = [-1, -1, -1]
    max_hsv = [-1, -1, -1]

    for i in range(256):
        for j in range(3):
            if hsv[j][i] != 0:
                max_hsv[j] = i
                if min_hsv[j] == -1:
                    min_hsv[j] = i

            if hsv[j][i] > limit:
                max_l_hsv[j] = i
                if min_l_hsv[j] == -1:
                    min_l_hsv[j] = i

    print('HSV Limited (Over {0} Pixels) Minimum range : {1}'.format(limit, min_l_hsv))
    print('HSV Limited (Over {0} Pixels) Maximum range : {1}'.format(limit, max_l_hsv))
    print('HSV Minimum range : {0}'.format(min_hsv))
    print('HSV Maximum range : {0}'.format(max_hsv))

    plt.plot(np.arange(256), hsv[0])
    plt.plot(np.arange(256), hsv[1])
    plt.plot(np.arange(256), hsv[2])
    plt.show()

    return tuple(min_l_hsv), tuple(max_l_hsv), tuple(min_hsv), tuple(max_hsv)


def check(frame_raw, low, high, name):
    frame = frame_raw.copy()

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, low, high)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), 1)

    cv2.imshow(name, mask)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    contour_sizes = []
    for contour in contours:
        contour_sizes.append(cv2.contourArea(contour))

    return contour_sizes


def check_dist(l, cell=100):
    dist = np.zeros(int(max(l) / 100) + 1)
    for i in l:
        dist[int(i / 100)] += 1
    return dist


def main():
    limit = int(input("Minimum Pixel Count to assume as Valid range : "))

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Get Maximum Resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 100000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100000)

    max_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    max_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print("Max Resolution : {0}x{1}".format(max_width, max_height))

    pause = False
    view = False
    position = [0, 0]

    ret = None
    frame = None
    frame_edit = None

    speed = 1
    radius = 10

    while True:
        if not pause:
            ret, frame = cap.read()

            if frame is None:
                print("Received Frame None")
                break

            frame = cv2.flip(frame, 1)

        key = cv2.waitKeyEx(1)

        # Space
        if key == 32:
            pause = not pause
        # Enter
        elif key == 13:
            if pause:
                if view:
                    cv2.destroyWindow('Limited')
                    cv2.destroyWindow('Full')
                    view = False
                    continue
                print('==========================================================================================')
                print("Area Selected of Center {0}x{1}, Radius {2} pixels".format(position[0], position[1], radius))
                min_l, max_l, min_r, max_r = calculate(frame, tuple(position), radius, limit)
                contours_l = check(frame, min_l, max_l, 'Limited')
                contours_r = check(frame, min_r, max_r, 'Full')
                print()
                print('HSV Limited (Over {0} Pixels) Range Test {1}'
                      .format(limit, 'Successful' if len(contours_l) == 1 else 'Failed'))
                print('Fount {0} Contours'.format(len(contours_l)))
                dist_l = check_dist(contours_l)
                for i in range(len(dist_l)):
                    if dist_l[i] == 0:
                        continue
                    print('{0} ~ {1} : {2} contours'.format(i * 100, (i + 1) * 100, dist_l[i]))
                print()
                print('HSV Range Test {1}'
                      .format(limit, 'Successful' if len(contours_r) == 1 else 'Failed'))
                print('Fount {0} Contours'.format(len(contours_r)))
                dist_r = check_dist(contours_r)
                for i in range(len(dist_r)):
                    if dist_r[i] == 0:
                        continue
                    print('{0} ~ {1} : {2} contours'.format(i * 100, (i + 1) * 100, dist_r[i]))
                view = True
            else:
                break

        if pause:
            # Left Arrow
            if key == 2424832:
                position[0] -= speed
                if position[0] < 0:
                    position[0] = 0
            # Right Arrow
            elif key == 2555904:
                position[0] += speed
                if position[0] > max_width:
                    position[0] = max_width
            # Up Arrow
            elif key == 2490368:
                position[1] -= speed
                if position[1] < 0:
                    position[1] = 0
            # Down Arrow
            elif key == 2621440:
                position[1] += speed
                if position[1] > max_height:
                    position[1] = max_height
            # Plus
            elif key == 43:
                radius += 1
            # Minus
            elif key == 45:
                radius -= 1
            elif 49 <= key <= 57:
                speed = key - 48
            frame_edit = frame.copy()
            cv2.circle(frame_edit, tuple(position), radius, (0, 0, 255), 3)
            cv2.imshow('Frame', frame_edit)
        else:
            cv2.imshow('Frame', frame)


if __name__ == '__main__':
    main()
