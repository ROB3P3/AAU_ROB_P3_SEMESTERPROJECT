import cv2
import numpy as np
import math
import IsolatingFish


def showImage(image):
    """Function to show an image until 0 is pressed"""
    cv2.imshow("Image", image)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)


def singleRGBcolor(color):
    """Function which converts single color to RGB. color -> [color, color, color]"""
    return [color, color, color]


def blobProperties(contours):
    """Function which returns a list of the properties of all blobs in an image.
    These properties include: The ID, the center position and radius of the encolsing circle, and the ellipse.
    It also returns a list containing the positions of the pixels with the minumum and maximum X- and Y-values."""
    properties = []
    positions = []
    fishID = 1

    # Goes through every blob
    for contourPixels in contours:

        pixelPositionX = []
        pixelPositionY = []
        averagePoint = []

        # Determines the area of the blob in order to avoid processing those too small to be fish
        area = cv2.contourArea(contourPixels)
        if area > 20000:
            # Finds the center and radius of the minimum enclosing circle
            (xc, yc), radius = cv2.minEnclosingCircle(contourPixels)
            # Pixel points have to be round numbers
            circleCenter = (round(xc), round(yc))

            # Fit an ellipce around the blob. Get
            ellipse = cv2.fitEllipse(contourPixels)
            ellipsePoints = ((round(ellipse[0][0]), round(ellipse[0][1])), (round(ellipse[1][0]), round(ellipse[1][1])))
            ellipseAngle = ellipse[2]
            print("eCenter: ", ellipsePoints, "angle: ", ellipseAngle)
            add = fishID, circleCenter, radius, ellipsePoints, ellipseAngle

            properties.append(add)

            for pixel in contourPixels:
                pixelPositionX.append(pixel[0][1])
                pixelPositionY.append(pixel[0][0])

            averagePointY = round(sum(pixelPositionX) / len(pixelPositionX))
            averagePointX = round(sum(pixelPositionY) / len(pixelPositionY))

            averagePoint.append((averagePointX, averagePointY))

            extremeLeft = tuple(contourPixels[contourPixels[:, :, 0].argmin()][0])
            extremeRight = tuple(contourPixels[contourPixels[:, :, 0].argmax()][0])
            extremeTop = tuple(contourPixels[contourPixels[:, :, 1].argmin()][0])
            extremeBottom = tuple(contourPixels[contourPixels[:, :, 1].argmax()][0])

            positions.append([extremeLeft, extremeRight, extremeTop, extremeBottom, averagePoint[0]])
            print("Positions: ", positions[fishID - 1])

            fishID += 1
    return properties, positions


def findSize(image):
    """Function to find the area and lenght of a fish(blob)"""

    fishLenght = []
    fishOrientation = []
    # List of RGB colors to differentiate between blobs later
    colours = [(230, 63, 7), (48, 18, 59), (68, 81, 191), (69, 138, 252), (37, 192, 231), (31, 233, 175),
               (101, 253, 105), (175, 250, 55), (227, 219, 56), (253, 172, 52), (246, 108, 25), (216, 55, 6),
               (164, 19, 1), (90, 66, 98), (105, 116, 203), (106, 161, 253), (81, 205, 236), (76, 237, 191),
               (132, 253, 135), (191, 251, 95), (233, 226, 96), (254, 189, 93), (248, 137, 71), (224, 95, 56),
               (182, 66, 52), (230, 63, 7), (48, 18, 59), (68, 81, 191), (69, 138, 252), (37, 192, 231), (31, 233, 175),
               (101, 253, 105), (175, 250, 55), (227, 219, 56), (253, 172, 52), (246, 108, 25), (216, 55, 6),
               (164, 19, 1), (90, 66, 98), (105, 116, 203), (106, 161, 253), (81, 205, 236), (76, 237, 191),
               (132, 253, 135), (191, 251, 95), (233, 226, 96), (254, 189, 93), (248, 137, 71), (224, 95, 56),
               (182, 66, 52)]
    invertedColors = []
    for i in range(len(colours)):
        invertedColors.append((255 - colours[i][0], 255 - colours[i][1], 255 - colours[i][2]))

    # Find contours of binary image
    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    sortedContours = sorted(contours, key=cv2.contourArea, reverse=True)

    blobsData, positions = blobProperties(sortedContours)

    imagePlot = image.copy()
    imagePlot = cv2.cvtColor(imagePlot, cv2.COLOR_GRAY2RGB)

    for i, data in enumerate(blobsData):
        fishID = data[0]
        centre = data[1]
        radius = data[2]
        ellipsePoints = data[3]
        ellipseAngle = round(data[4])

        averagePoint = positions[i][4]
        mininumPointX = positions[i][0]
        maximumPointX = positions[i][1]
        mininumPointY = positions[i][2]
        maximumPointY = positions[i][3]
        pointsMinMaxXY = [mininumPointX, maximumPointX, mininumPointY, maximumPointY]

        cv2.drawContours(imagePlot, [sortedContours[i]], -1, colours[i], -1)  # , colours[i], thickness=cv2.FILLED)

        lineColor = singleRGBcolor(255)

        lenghtCircle = radius * 2
        print("Circle lenght: ", lenghtCircle)

        # Calculate distance from average point to extremepoints
        lenght2MinX = math.sqrt((mininumPointX[0] - averagePoint[0]) ** 2 + (mininumPointX[1] - averagePoint[1]) ** 2)
        lenght2MaxX = math.sqrt((maximumPointX[0] - averagePoint[0]) ** 2 + (maximumPointX[1] - averagePoint[1]) ** 2)
        lenght2MinY = math.sqrt((mininumPointY[0] - averagePoint[0]) ** 2 + (mininumPointY[1] - averagePoint[1]) ** 2)
        lenght2MaxY = math.sqrt((maximumPointY[0] - averagePoint[0]) ** 2 + (maximumPointY[1] - averagePoint[1]) ** 2)
        lenghts = [lenght2MinX, lenght2MaxX, lenght2MinY, lenght2MaxY]

        # Calculate and show lenght in GUI

        print("Lenghts: ", lenghts, sorted(lenghts))
        extremePoint1Index = lenghts.index(sorted(lenghts)[3])
        extremePoint1 = pointsMinMaxXY[extremePoint1Index]
        extremePoint2Index = lenghts.index(sorted(lenghts)[2])
        extremePoint2 = pointsMinMaxXY[extremePoint2Index]

        # Calculate distance between extremePoint1 and extremePoint2
        lenghtBetweenExtremes = math.sqrt(
            (extremePoint2[0] - extremePoint1[0]) ** 2 + (extremePoint2[1] - extremePoint1[1]) ** 2)

        if lenghtBetweenExtremes < 200:
            lenghts[lenghts.index(sorted(lenghts)[2])] = 0
            extremePoint2Index = lenghts.index(sorted(lenghts)[2])
            extremePoint2 = pointsMinMaxXY[extremePoint2Index]

        print("Distance between extreme points: ", lenghtBetweenExtremes)

        totalLenght = float(sum(sorted(lenghts)[2:]))

        # Plot lines to extreme points, and mark the lines chosen.
        cv2.line(imagePlot, averagePoint, mininumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, mininumPointY, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointY, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePoint1, invertedColors[i], 3)
        cv2.line(imagePlot, averagePoint, extremePoint2, invertedColors[i], 3)

        convertedLenght = float((totalLenght * 0.4) / 10)
        print("Totallenght: ", totalLenght, radius * 2, "Converted lenght: ", convertedLenght)

        cv2.putText(imagePlot, str(round(convertedLenght, 1)) + "CM", averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(convertedLenght, 1)) + "CM", averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)

        """cv2.putText(imagePlot, str(round(convertedLenghtCircle, 1)) + "CM C", (averagePoint[0], averagePoint[1] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(convertedLenghtCircle, 1)) + "CM C", (averagePoint[0], averagePoint[1] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)"""

        fishText = "Fish" + str(fishID)
        cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    invertedColors[i], 2, cv2.LINE_AA)

        fishLenght.append(totalLenght)

        # Find orientation of fish.

        angle1 = (math.atan2((extremePoint1[1] - averagePoint[1]),
                             (extremePoint1[0] - averagePoint[0]))) * 180 / math.pi
        angle2 = (math.atan2((extremePoint2[1] - averagePoint[1]),
                             (extremePoint2[0] - averagePoint[0]))) * 180 / math.pi
        angles = (angle1, angle2)
        print(angles)

        cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    invertedColors[i], 2, cv2.LINE_AA)

        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    invertedColors[i], 2, cv2.LINE_AA)

        fishOrientation.append(angles)

    # print(fishLenght)
    # showImage(imagePlot)
    return fishLenght, fishOrientation


if __name__ == "__main__":
    image = cv2.imread(r"DATAdir/RGB/tiff/00016.tiff", cv2.IMREAD_GRAYSCALE)
    imageThreshold = IsolatingFish.isolateFish(image)

    # imageThreshold = cv2.imread(r"DATAdir/RGB/tiff/00016binary.tiff", cv2.IMREAD_UNCHANGED)
    findSize(imageThreshold)
