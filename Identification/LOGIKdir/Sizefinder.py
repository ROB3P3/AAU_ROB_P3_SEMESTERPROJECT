import glob
import cv2
import numpy as np
import math


def showImage(images):
    """Function to show an array of images until 0 is pressed"""
    for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 48:
            break
        # print(k)


def browseImages(imageList):
    """Function to show an image until left or right arrow is pressed, then show the next or previous image in the array."""
    i = 0
    while True:
        cv2.imshow("Image", imageList[i])
        k = cv2.waitKey(0) & 0xFF
        print(k)
        if k == 52:
            if i > 0:
                cv2.setWindowTitle("Image", "Image{}".format(i))
                i -= 1
        elif k == 54:
            if i < len(imageList) - 1:
                cv2.setWindowTitle("Image", "Image{}".format(i + 2))
                i += 1
        elif k == 48:
            break
        print(i)


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
    for contour in contours:

        pixelPositionX = []
        pixelPositionY = []
        averagePoint = []

        # Determines the area of the blob in order to avoid processing those too small to be fish
        area = cv2.contourArea(contour)
        if area > 5000:
            add = fishID

            properties.append(add)

            # Get all pixel positions in contour to calculate average point
            extracted = np.zeros((1080, 1080), np.uint8)
            extracted = cv2.drawContours(extracted, [contour], -1, 255, -1)
            yPixelValues, xPixelValues = np.nonzero(extracted)
            # combine the x and y values into a list of tuples
            pixelValues = list(zip(xPixelValues, yPixelValues))

            # Calculate the average x and y values to get the average point in the blob
            averagePointX = round(sum(xPixelValues) / len(xPixelValues))
            averagePointY = round(sum(yPixelValues) / len(yPixelValues))
            averagePoint.append((averagePointX, averagePointY))

            # Find extreme points in contour. If multiple points have the same value, the middle point is used.
            extremeRightIndex = np.where(xPixelValues == np.amax(xPixelValues))[0]
            extremeRightIndex = extremeRightIndex[len(extremeRightIndex) // 2]
            extremeBottomIndex = np.where(yPixelValues == np.amax(yPixelValues))[0]
            extremeBottomIndex = extremeBottomIndex[len(extremeBottomIndex) // 2]
            extremeLeftIndex = np.where(xPixelValues == np.amin(xPixelValues))[0]
            extremeLeftIndex = extremeLeftIndex[len(extremeLeftIndex) // 2]
            extremeTopIndex = np.where(yPixelValues == np.amin(yPixelValues))[0]
            extremeTopIndex = extremeTopIndex[len(extremeTopIndex) // 2]

            # take the first of the index for the extreme points to get the average points.
            extremeRight = (xPixelValues[extremeRightIndex], yPixelValues[extremeRightIndex])
            extremeBottom = (xPixelValues[extremeBottomIndex], yPixelValues[extremeBottomIndex])
            extremeLeft = (xPixelValues[extremeLeftIndex], yPixelValues[extremeLeftIndex])
            extremeTop = (xPixelValues[extremeTopIndex], yPixelValues[extremeTopIndex])

            print("Extreme left: ", extremeLeft)
            print("Extreme right: ", extremeRight)
            print("Extreme top: ", extremeTop)
            print("Extreme bottom: ", extremeBottom)
            print("Average point: ", averagePoint[0])
            # showImage([extracted])

            """extremeLeft = tuple(contour[contour[:, :, 0].argmin()][0])
            extremeRight = tuple(contour[contour[:, :, 0].argmax()][0])
            extremeTop = tuple(contour[contour[:, :, 1].argmin()][0])
            extremeBottom = tuple(contour[contour[:, :, 1].argmax()][0])"""

            positions.append([extremeLeft, extremeRight, extremeTop, extremeBottom, averagePoint[0]])
            print("Positions: ", positions[fishID - 1])

            fishID += 1

    return properties, positions


def findSize(image):
    """Function to find the area and lenght of a fish(blob). image -> binary"""

    fishLenght = []
    fishOrientation = []
    averagePoints = []
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

    # Find contours (blobs) of binary image
    contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # idfk hvorfor det her sker, måske pga. det er binær.
    contours = contours[0] if len(contours) == 2 else contours[1]

    sortedContours = sorted(contours, key=cv2.contourArea, reverse=True)

    blobsData, positions = blobProperties(sortedContours)

    imagePlot = image.copy()
    imagePlot = cv2.cvtColor(imagePlot, cv2.COLOR_GRAY2RGB)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    for i, fishID in enumerate(blobsData):

        averagePoint = positions[i][4]
        mininumPointX = positions[i][0]
        maximumPointX = positions[i][1]
        mininumPointY = positions[i][2]
        maximumPointY = positions[i][3]
        pointsMinMaxXY = [mininumPointX, maximumPointX, mininumPointY, maximumPointY]
        print("Points min max: ", pointsMinMaxXY)

        cv2.drawContours(imagePlot, [sortedContours[i]], -1, (255, 255, 255), -1)  # , colours[i], thickness=cv2.FILLED)

        lineColor = singleRGBcolor(round(255 / 2))

        print("Drawing average point: ", averagePoint)

        cv2.circle(imagePlot, averagePoint, 5, (255, 0, 0), -1)

        # Calculate distance from average point to extremepoints
        lenght2MinX = math.sqrt((mininumPointX[0] - averagePoint[0]) ** 2 + (mininumPointX[1] - averagePoint[1]) ** 2)
        lenght2MaxX = math.sqrt((maximumPointX[0] - averagePoint[0]) ** 2 + (maximumPointX[1] - averagePoint[1]) ** 2)
        lenght2MinY = math.sqrt((mininumPointY[0] - averagePoint[0]) ** 2 + (mininumPointY[1] - averagePoint[1]) ** 2)
        lenght2MaxY = math.sqrt((maximumPointY[0] - averagePoint[0]) ** 2 + (maximumPointY[1] - averagePoint[1]) ** 2)
        lenghts = [lenght2MinX, lenght2MaxX, lenght2MinY, lenght2MaxY]
        # If any of the values in lenght is equal to another value, add 0.0001 to one of them.
        for j, lenght in enumerate(lenghts):
            for l, lenght2 in enumerate(lenghts):
                if lenght == lenght2 and j != l:
                    lenghts[j] += 0.0001



        # Determine the 2 most points furthest from the average point
        print("Lenghts: ", lenghts, sorted(lenghts))
        extremePoint1Index = lenghts.index(sorted(lenghts, reverse=True)[0])
        extremePoint1 = pointsMinMaxXY[extremePoint1Index]
        print("Extreme point 1: ", extremePoint1, "Index: ", extremePoint1Index)
        extremePoint2Index = lenghts.index(sorted(lenghts, reverse=True)[1])
        extremePoint2 = pointsMinMaxXY[extremePoint2Index]
        print("Extreme point 2: ", extremePoint2, "Index: ", extremePoint2Index)

        # Calculate angle between from averagfrom the average point.
        # Find orientation of fish head and tail (cannot determine which is which).
        angle1 = (math.atan2((extremePoint1[1] - averagePoint[1]),
                             (extremePoint1[0] - averagePoint[0]))) * 180 / math.pi
        angle2 = (math.atan2((extremePoint2[1] - averagePoint[1]),
                             (extremePoint2[0] - averagePoint[0]))) * 180 / math.pi
        angleBetweenExtremes = angle1 - angle2
        angles = (angle1, angle2)
        print("Angle between extremes: ", angleBetweenExtremes)

        # If the angle between extreme point 2 and extreme point 1 is less that 45 degrees,
        # then use the extreme point which is third furthest away from the average point as extreme point 2.
        if -90 < angleBetweenExtremes < 90 or -270 > angleBetweenExtremes > -360 or 270 < angleBetweenExtremes < 360:
            print("Sorted lists")
            print(sorted(lenghts, reverse=True))
            lenghts[lenghts.index(sorted(lenghts, reverse=True)[1])] = 0
            print(sorted(lenghts, reverse=True))
            extremePoint2Index = lenghts.index(sorted(lenghts, reverse=True)[1])
            extremePoint2 = pointsMinMaxXY[extremePoint2Index]
            print("Extreme point 2: ", extremePoint2, "Index: ", extremePoint2Index)
            angle2 = (math.atan2((extremePoint2[1] - averagePoint[1]),
                                 (extremePoint2[0] - averagePoint[0]))) * 180 / math.pi
            angleBetweenExtremes = angle1 - angle2


        # calculate total pixel lenght of fish.
        totalLenght = float(sum(sorted(lenghts)[2:]))

        # Plot lines to extreme points, and mark the lines chosen.
        cv2.line(imagePlot, averagePoint, mininumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, mininumPointY, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointY, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePoint1, invertedColors[i], 3)
        cv2.line(imagePlot, averagePoint, extremePoint2, invertedColors[i], 3)

        # convert pixel lenght to centimeters.
        # convertedLenght = float((totalLenght * 0.4) / 10)
        convertedLenght = round(totalLenght)

        print("Totallenght: ", totalLenght, "Converted lenght: ", convertedLenght)

        cv2.putText(imagePlot, str(round(convertedLenght, 1)), averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(convertedLenght, 1)), averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # possible use though unsure
        # Using circles for lenght estimation
        """cv2.putText(imagePlot, str(round(convertedLenghtCircle, 1)) + "CM C", (averagePoint[0], averagePoint[1] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(convertedLenghtCircle, 1)) + "CM C", (averagePoint[0], averagePoint[1] - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)"""

        # Label blobs
        fishText = "Fish" + str(fishID)
        """cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)"""

        fishLenght.append(totalLenght)

        # put angles on the lines to show.
        """cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)

        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)"""

        fishOrientation.append(angles)
        averagePoints.append(averagePoint)

    # print(fishLenght)

    return fishLenght, fishOrientation, averagePoints, imagePlot


if __name__ == "__main__":
    images = glob.glob(r"C:/Users/klump/OneDrive/Billeder/Fishtestdata/Shape tool/Org/*.png")
    imageList = []
    print(images)
    for i, fileName in enumerate(images):
        # Get png name and remove png ending
        name = fileName.rsplit('\\', 1)[-1]
        name = name[:-4]
        print(name)

        image = cv2.imread(fileName, cv2.IMREAD_GRAYSCALE)
        # imageThreshold = IsolatingFish.isolateFish(image)
        fishLenghts, fishOrientations, averagePoints, annotatedImage = findSize(image)
        annotatedImage = cv2.resize(annotatedImage, (960, 960))
        imageList.append(annotatedImage)
        """cv2.imwrite(
            "C:/Users/klump/OneDrive/Billeder/Fishtestdata/Shape tool/Comparison/" + name + "Program.png",
            annotatedImage)"""

    browseImages(imageList)
