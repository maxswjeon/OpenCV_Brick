try:
    from cv2 import cv2
except ImportError:
    pass


def main():
    while True:
        low = (100, 20, 6)
        high = (150, 75, 255)

        image = cv2.imread('17737889.jpg')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, low, high)
        res = cv2.bitwise_and(image, image, mask=mask)

        cv2.imshow("Result", res)
        if cv2.waitKey(1) > 0:
            break

if __name__ == "__main__":
    main()
