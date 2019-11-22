import cv2


def main():
    low = (48, 86, 6)
    high = (64, 255, 255)

    image = cv2.imread('test.bmp')
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    res = cv2.bitwise_and(image, image, mask=mask)
    cv2.imwrite("Result.png", res)


if __name__ == "__main__":
    main()
