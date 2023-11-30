import glob
import cv2
import numpy as np
import math
import IsolatingFish2
import os
import time
import multiprocessing as mp
from fractions import Fraction


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


def blobProperties(contours, y, x):
    """Function which returns a list of the properties of all blobs in an image.
    These properties include: The ID, the center position and radius of the encolsing circle, and the ellipse.
    It also returns a list containing the positions of the pixels with the minumum and maximum X- and Y-values."""
    properties = []
    positions = []
    separateContours = []
    fishID = 1

    # Goes through every blob
    for contour in contours:
        averagePoint = []

        # Determines the area of the blob in order to avoid processing those too small to be fish
        area = cv2.contourArea(contour)
        if area > 5000:
            add = fishID

            properties.append(add)

            # Get all pixel positions in contour to calculate average point
            extracted = np.zeros((y, x), np.uint8)
            extracted = cv2.drawContours(extracted, [contour], -1, 255, -1)
            separateContours.append(extracted)
            yPixelValues, xPixelValues = np.nonzero(extracted)

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

            positions.append([extremeLeft, extremeRight, extremeTop, extremeBottom, averagePoint[0]])

            fishID += 1

    return properties, positions, separateContours


def findSize(image, originalImage):
    """Function to find the area and lenght of a fish(blob). image -> binary"""

    fishLenght = []
    fishOrientation = []
    averagePoints = []
    extremePointList = []
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

    y = image.shape[0]
    x = image.shape[1]
    blobsData, positions, separateContours = blobProperties(sortedContours, y, x)

    imagePlot = image.copy()
    imagePlot = cv2.cvtColor(imagePlot, cv2.COLOR_GRAY2RGB)
    for i, fishID in enumerate(blobsData):

        averagePoint = positions[i][4]
        extremePointLeft = positions[i][0]
        extremePointRight = positions[i][1]
        extremePointTop = positions[i][2]
        extremePointBottom = positions[i][3]
        extremePointList = [extremePointLeft, extremePointRight, extremePointTop, extremePointBottom]

        originalImage = cv2.rectangle(originalImage, [extremePointLeft[0], extremePointTop[1]],
                                      [extremePointRight[0], extremePointBottom[1]], colours[i], 2)

        cv2.drawContours(imagePlot, [sortedContours[i]], -1, colours[i], -1)  # , colours[i], thickness=cv2.FILLED)

        lineColor = singleRGBcolor(round(255 / 2))

        # Plot average point
        cv2.circle(imagePlot, averagePoint, 5, (255, 0, 0), -1)

        # Calculate distance from average point to extremepoints
        lenght2MinX = math.sqrt(
            (extremePointLeft[0] - averagePoint[0]) ** 2 + (extremePointLeft[1] - averagePoint[1]) ** 2)
        lenght2MaxX = math.sqrt(
            (extremePointRight[0] - averagePoint[0]) ** 2 + (extremePointRight[1] - averagePoint[1]) ** 2)
        lenght2MinY = math.sqrt(
            (extremePointTop[0] - averagePoint[0]) ** 2 + (extremePointTop[1] - averagePoint[1]) ** 2)
        lenght2MaxY = math.sqrt(
            (extremePointBottom[0] - averagePoint[0]) ** 2 + (extremePointBottom[1] - averagePoint[1]) ** 2)
        lenghts = [lenght2MinX, lenght2MaxX, lenght2MinY, lenght2MaxY]
        # If any of the values in lenght is equal to another value, add 0.0001 to one of them.
        for j, lenght in enumerate(lenghts):
            for l, lenght2 in enumerate(lenghts):
                if lenght == lenght2 and j != l:
                    lenghts[j] += 0.0001

        # Determine the 2 most points furthest from the average point
        extremePoint1Index = lenghts.index(sorted(lenghts, reverse=True)[0])
        extremePoint1 = extremePointList[extremePoint1Index]
        extremePoint2Index = lenghts.index(sorted(lenghts, reverse=True)[1])
        extremePoint2 = extremePointList[extremePoint2Index]

        # Calculate angle between from averagfrom the average point.
        # Find orientation of fish head and tail (cannot determine which is which).
        angle1 = (math.atan2((extremePoint1[1] - averagePoint[1]),
                             (extremePoint1[0] - averagePoint[0]))) * 180 / math.pi
        angle2 = (math.atan2((extremePoint2[1] - averagePoint[1]),
                             (extremePoint2[0] - averagePoint[0]))) * 180 / math.pi
        angleBetweenExtremes = angle1 - angle2
        angles = (angle1, angle2)

        # If the angle between extreme point 2 and extreme point 1 is less that 45 degrees,
        # then use the extreme point which is third furthest away from the average point as extreme point 2.
        if -90 < angleBetweenExtremes < 90 or -270 > angleBetweenExtremes > -360 or 270 < angleBetweenExtremes < 360:
            print("Sorted lists")
            print(sorted(lenghts, reverse=True))
            lenghts[lenghts.index(sorted(lenghts, reverse=True)[1])] = 0
            print(sorted(lenghts, reverse=True))
            extremePoint2Index = lenghts.index(sorted(lenghts, reverse=True)[1])
            extremePoint2 = extremePointList[extremePoint2Index]
            print("Extreme point 2: ", extremePoint2, "Index: ", extremePoint2Index)
            angle2 = (math.atan2((extremePoint2[1] - averagePoint[1]),
                                 (extremePoint2[0] - averagePoint[0]))) * 180 / math.pi

        # calculate total pixel lenght of fish.
        totalLenght = float(sum(sorted(lenghts)[2:]))

        # Plot lines to extreme points, and mark the lines chosen.
        cv2.line(imagePlot, averagePoint, extremePointLeft, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePointRight, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePointTop, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePointBottom, lineColor, 2)
        cv2.line(imagePlot, averagePoint, extremePoint1, invertedColors[i], 3)
        cv2.line(imagePlot, averagePoint, extremePoint2, invertedColors[i], 3)

        # convert pixel lenght to centimeters.
        # convertedLenght = float((totalLenght * 0.4) / 10)
        convertedLenght = round(totalLenght)

        print("Totallenght: ", totalLenght, "Converted lenght: ", convertedLenght)

        cv2.putText(imagePlot, str(round(convertedLenght, 1)), (averagePoint[0], averagePoint[1] + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(convertedLenght, 1)), (averagePoint[0], averagePoint[1] + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # Label blobs
        fishText = "Fish" + str(fishID)
        cv2.putText(imagePlot, fishText, averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, fishText, averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)

        fishLenght.append(totalLenght)

        # put angles on the lines to show.
        cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle1)), extremePoint1, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)

        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(angle2)), extremePoint2, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    invertedColors[i], 1, cv2.LINE_AA)

        fishOrientation.append(angles)
        averagePoints.append(averagePoint)

    return fishLenght, fishOrientation, imagePlot, originalImage, averagePoints, separateContours, extremePointList


def pathingSetup(group, rootPath):
    if not os.path.exists("{}/group_{}/Size".format(rootPath, group)):
        os.makedirs("{}/group_{}/Size".format(rootPath, group))
    if not os.path.exists("{}/group_{}/THData".format(rootPath, group)):
        os.makedirs("{}/group_{}/THData".format(rootPath, group))
    if not os.path.exists("{}/group_{}/FinalTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/FinalTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/DepthTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/DepthTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/CP".format(rootPath, group)):
        os.makedirs("{}/group_{}/CP".format(rootPath, group))
    if not os.path.exists("{}/group_{}/Edge".format(rootPath, group)):
        os.makedirs("{}/group_{}/Edge".format(rootPath, group))
    if not os.path.exists("{}/group_{}/ColourTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/ColourTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/THSum".format(rootPath, group)):
        os.makedirs("{}/group_{}/THSum".format(rootPath, group))


def taskHandeler(indexFileNameList, startingNumber, group, outputDataRootPath):
    for i, fileName in enumerate(indexFileNameList):
        i += startingNumber
        imageThreshold = cv2.imread(fileName, cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(fileName)
        imageThreshold = IsolatingFish2.isolate(fileName, i + 1, group, outputDataRootPath)
        fishLenghts, fishOrientations, annotatedImage, boundingBoxImage, averagePoints, separateContours, extremePoints = findSize(
            imageThreshold, image)
        # annotatedImageS = cv2.resize(annotatedImage, (0, 0), fx = 0.5, fy = 0.5)
        # imageS = cv2.resize(image, (0, 0), fx = 0.5, fy = 0.5)
        print(fileName)
        # showImage([imageS, annotatedImageS])

        os.chdir("{}/group_{}/Size".format(outputDataRootPath, group))
        cv2.imwrite("size" + str(i + 1) + ".png", annotatedImage)
        cv2.imwrite("OG" + str(i + 1) + ".png", boundingBoxImage)


if __name__ == "__main__":
    startTime = time.time()
    groups = [10]  # [10, 14, 20, 21, 22] # The groups the program is goinf through

    for group in groups:
        pathInputRoot = "C:/Users/fhp89/OneDrive - Aalborg Universitet/autofish_rob3"
        images = glob.glob(
            "{}/group_{}/rs/rgb/*.png".format(pathInputRoot, group))  # OBS!!!!! Change to directory to Data set png's
        outputDataRootPath = "D:/P3OutData/Merged"  # where you want the program to create it's data folders
        pathingSetup(group, outputDataRootPath)
        numberOfThreads = 12  # OBS!!!!! chose the amount of threds to use
        picturesPerGroup = 66

        process = []
        indexJump = int(math.modf(66 / numberOfThreads)[1])
        optimizeFraction = Fraction(math.modf(66 / numberOfThreads)[0]).limit_denominator(1000000)
        Offset = (numberOfThreads / optimizeFraction.denominator) * optimizeFraction.numerator
        indexOffsetEnd = 0
        indexOffsetStart = 0
        for i in range(numberOfThreads):
            if Offset != 0:
                indexOffsetEnd += 1
                Offset -= 1
            if i == 0:
                if Offset != 0:
                    indexOffsetEnd += 1
                    Offset -= 1
                process.append(mp.Process(target=taskHandeler,
                                          args=(images[1:indexJump + indexOffsetEnd], 1, group, outputDataRootPath)))
            elif i == numberOfThreads - 1:
                process.append(mp.Process(target=taskHandeler, args=(
                images[i * indexJump + indexOffsetStart:67], i * indexJump + indexOffsetStart, group,
                outputDataRootPath)))
            else:
                process.append(mp.Process(target=taskHandeler, args=(
                images[i * indexJump + indexOffsetStart:(i + 1) * indexJump + indexOffsetEnd],
                i * indexJump + indexOffsetStart, group, outputDataRootPath)))

        for element in process:
            element.start()

        for element in process:
            element.join()

    print("TIME:", str(startTime - time.time()))
