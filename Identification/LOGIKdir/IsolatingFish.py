import cv2
import numpy as np
import math
from PIL import Image, ImageFilter


def showImage(images):
    """Function to show an array of images until 0 is pressed"""
    for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)


# function to fill the holes in the image
def fillHoles(image):
    imCopy = image.copy()

    h, w = imCopy.shape[:2]
    imMask = np.zeros((h + 2, w + 2), np.uint8)

    cv2.floodFill(imCopy, imMask, (0, 0), 255)

    imCopy = cv2.bitwise_not(imCopy)

    imReturn = image | imCopy

    return imReturn


# function to remove the sides of the conveyor belt in the tiff images
def removeSides(image):
    # manually found the x-coordinates for the sides on the top and bottom
    xLeftTop = 666
    xLeftBot = 677
    xRightTop = 1824
    xRightBot = 1864

    for y, row in enumerate(image):
        for x, col in enumerate(row):
            # since the image is crooked, the sides are removed by scaling the difference in the x-coordinates with the y-coordinate
            if x <= (xLeftTop + math.floor((((xLeftBot - xLeftTop) / 2056) * y))) or x >= (
                    xRightTop + math.floor((((xRightBot - xRightTop) / 2056) * y))):
                image[y][x] = 0

    return image


def isolateFish(img):
    # 1st step: median blur with radius 10
    print("Original image")
    img = cv2.medianBlur(img, (5 * 2) + 1)
    print("Median blur 1")
    # 2nd step: unsharp masking with radius 20, and mask weight of 0.9
    img = Image.fromarray(img)
    img = img.filter(ImageFilter.UnsharpMask(radius=10, percent=900))
    img = np.array(img)
    print("Unsharpen")
    # 3rd step: thresholding between 0 - 125
    ret, img = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY_INV)
    print("Threshold")

    # 6th step: median blur with radius 5
    print("Median blur 2")
    img = cv2.medianBlur(img, (5 * 2) + 1)

    # 5th step: filling the holes in the image
    img = fillHoles(img)

    print("Median blur 3")
    #img = cv2.medianBlur(img, (5 * 2) + 1)

    return img


if __name__ == "__main__":
    # 1080 x 1080 pixel images
    img = cv2.imread(r"DATAdir/RGB/Group9/WarpedCalibratedFish/calibrated00008.png", cv2.IMREAD_GRAYSCALE)
    isolatedImage = isolateFish(img)
    print("Done")
    showImage([isolatedImage])
    # showing the images at each step
    # cv2.imshow("image", img)
    # cv2.imshow("median blur 1", medianBlur)
    # cv2.imshow("unsharp maske", unsharpenedImage)
    # cv2.imshow("thresholding", thresholdedImage)
    # cv2.imshow("median blur 2", medianBlur2)

    # radius of nxn matrix :
    # r = (n-1)/2
    # n = (r*2) + 1
