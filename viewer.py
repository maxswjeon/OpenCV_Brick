try:
    from cv2 import cv2
except ImportError:
    pass
import json
import numpy


def main():
    f = open("log.json", "r")
    data_str = f.read()
    f.close()
    data = json.loads(data_str)

    image = 255 * numpy.ones(shape=[1280, 720, 3], dtype=numpy.uint8)

    for c in data:
        cv2.circle(image, (c["x"], c["y"]), 1, (255, 0, 0), -1)

    cv2.imshow("Result", image)

    while cv2.waitKey(1) < 0:
        pass


if __name__ == "__main__":
    main()
