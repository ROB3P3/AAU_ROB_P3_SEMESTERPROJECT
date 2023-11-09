import cv2
import numpy as np
import math
from PIL import Image, ImageFilter



# function to fill the holes in the image
def fillHoles(image):
    imCopy = image.copy()
    h, w = imCopy.shape[:2]
    imMask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(imCopy, imMask, (0,0), 255)

    imCopy = cv2.bitwise_not(imCopy)

    imReturn = image | imCopy
    return imReturn

# function to remove the sides of the conveyor belt in the tiff images
def removeSides(image):
    # manually found the x-coordinates for the sides on the top and bottom
    xLeftTop = 80
    xLeftBot = 105
    xRightTop = 2347
    xRightBot  = 2370
    
    for y, row in enumerate(image):
        for x, col in enumerate(row):
            # since the image is crooked, the sides are removed by scaling the difference in the x-coordinates with the y-coordinate
            if x <= (xLeftTop + math.floor((((xLeftBot - xLeftTop) / 2056) * y))) or x >= (xRightTop + math.floor((((xRightBot - xRightTop) / 2056) * y))):
                image[y][x] = 0
    
    return image

def isolateFish(img):
    # 1st step: median blur with radius 20
    medianBlur = cv2.medianBlur(img, (20*2)+1)
    # 2nd step: unsharp masking with radius 20, and mask weight of 0.9
    unsharpenedImage = Image.fromarray(medianBlur)
    unsharpenedImage = unsharpenedImage.filter(ImageFilter.UnsharpMask(radius=20, percent=900))
    unsharpenedImage = np.array(unsharpenedImage)
    # 3rd step: thresholding between 0 - 125
    ret, thresholdedImage = cv2.threshold(unsharpenedImage, 125, 255, cv2.THRESH_BINARY_INV)
    # 4th step: removing the sides
    thresholdedImage = removeSides(thresholdedImage)
    # 5th step: median blur with radius 20
    medianBlur2 = cv2.medianBlur(thresholdedImage, (20*2)+1)
    # 6th step: filling the holes in the image
    holedImage = fillHoles(medianBlur2)

    return holedImage

if __name__ == "__main__":
    # 2464 x 2056 pixel images
    img = cv2.imread(r"DATAdir/RGB/tiff/00016.tiff", cv2.IMREAD_GRAYSCALE)

    holedImage = isolateFish(img)
    # showing the images at each step
    #cv2.imshow("image", img)
    #cv2.imshow("median blur 1", medianBlur)
    #cv2.imshow("unsharp maske", unsharpenedImage)
    #cv2.imshow("thresholding", thresholdedImage)
    #cv2.imshow("median blur 2", medianBlur2)
    cv2.imshow("holed image", holedImage)
    cv2.waitKey(0)

    # radius of nxn matrix :
    # r = (n-1)/2
    # n = (r*2) + 1