import glob
import cv2
import numpy as np
import math
import os
import time
import multiprocessing as mp
from fractions import Fraction


class SizeFinder:
    def __init__(self) -> None:
        print("Sizefinder initialized:")

    def showImage(self, images):
        """Function to show an array of images until 0 is pressed"""
        for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
        while True:
            k = cv2.waitKey(0) & 0xFF
            if k == 48:
                break
            # print(k)

    def browseImages(self, imageList):
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

    def blobProperties(self, contours, y, x):
        """Function which returns a list of the properties of all blobs in an image.
        It also returns a list containing the positions of the pixels with the minumum and maximum X- and Y-values."""
        properties = []
        positions = []
        separateContours = []
        fishID = 1

        # Goes through every blob
        for contour in contours:
            properties.append([])
            averagePoint = []
            properties[fishID-1].append(fishID)

            # Get all pixel positions in contour to calculate average point
            extracted = np.zeros((y, x), np.uint8)
            extracted = cv2.drawContours(extracted, [contour], -1, 255, -1)
            # self.showImage([extracted])

            # Get all pixel positions in contour to calculate average point
            extracted = np.zeros((y, x), np.uint8)
            extracted = cv2.drawContours(extracted, [contour], -1, 255, -1)
            # self.showImage([extracted])

            # Make a copy of the blobs in RGB to use as a comparison image
            blobsRGB = extracted.copy()
            blobsRGB = cv2.cvtColor(blobsRGB, cv2.COLOR_GRAY2RGB)

            # Make a copy of the image to draw on
            boundedContours = extracted.copy()

            # Find the convex hull of the contour, withouth returning the points so that it can be used to find the convexity defects
            hull = cv2.convexHull(contour, returnPoints=False)

            # Find the convexity defects of the contour and use them to draw the convex hull
            defects = cv2.convexityDefects(contour, hull)
            for i in range(defects.shape[0]):
                blackPixels = 0

                # Get the start, end, and far points of the convexity defect
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])

                # Draw a triangle with the start, end, and far points
                triangle = np.array([start, end, far])

                # Draw that triangle on a blank image and get the pixel positions of the triangle
                extractedTriangle = np.zeros((y, x), np.uint8)
                extractedTriangle = cv2.drawContours(extractedTriangle, [triangle], -1, 255, -1)
                yPixelValuesTriangle, xPixelValuesTriangle = np.nonzero(extractedTriangle)
                # go through every pixel of the triangle and count the amount of black pixels in the original contour
                for j in range(len(xPixelValuesTriangle)):
                    if all(blobsRGB[yPixelValuesTriangle[j]][xPixelValuesTriangle[j]]) == 0:
                        # print("black pixel")
                        blackPixels += 1
                # print("Percentage of black pixels: ", blackPixels/len(xPixelValuesTriangle))

                # Calculate the lenght of the line from the start to the end point
                lenght = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)

                # If the percentage of black pixels in the triangle is greater than 75% and the lenght of the line is greater than 100 pixels
                # then draw the line from both the start adnd end point to the far point instead of from the start to the end point
                if blackPixels / len(xPixelValuesTriangle) > 0.75 and lenght > 100:

                    cv2.line(boundedContours, start, far, 255, 2)
                    cv2.line(boundedContours, end, far, 255, 2)

                else:
                    cv2.line(boundedContours, start, end, 255, 2)

            # Extract the new bounded contour
            boundedContours = cv2.findContours(boundedContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

            extractedBounded = np.zeros((y, x), np.uint8)
            extractedBounded = cv2.drawContours(extractedBounded, [boundedContours[0]], -1, 255, -1)
            # Get all pixel positions in contour to calculate average point
            yPixelValues, xPixelValues = np.nonzero(extractedBounded)
            # print(yPixelValues, xPixelValues)
            # self.showImage([extractedBounded])

            # Add each bounded contour to a list so they can be accessed separately
            separateContours.append(boundedContours)

            # Get area of bounded contour
            area = cv2.contourArea(boundedContours[0])
            properties[fishID-1].append(area)


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

    def findSize(self, imageData):
        """Function to find the area and lenght of a fish(blob). image -> binary"""
        image = imageData.filledThresholdedImage

        fishLenght = []
        fishOrientation = []
        averagePoints = []
        extremePoint1List = []
        extremePoint2List = []
        # List of RGB colors to differentiate between blobs later
        colours = [(230, 63, 7), (48, 18, 59), (68, 81, 191), (69, 138, 252), (37, 192, 231), (31, 233, 175),
                   (101, 253, 105), (175, 250, 55), (227, 219, 56), (253, 172, 52), (246, 108, 25), (216, 55, 6),
                   (164, 19, 1), (90, 66, 98), (105, 116, 203), (106, 161, 253), (81, 205, 236), (76, 237, 191),
                   (132, 253, 135), (191, 251, 95), (233, 226, 96), (254, 189, 93), (248, 137, 71), (224, 95, 56),
                   (182, 66, 52), (230, 63, 7), (48, 18, 59), (68, 81, 191), (69, 138, 252), (37, 192, 231),
                   (31, 233, 175),
                   (101, 253, 105), (175, 250, 55), (227, 219, 56), (253, 172, 52), (246, 108, 25), (216, 55, 6),
                   (164, 19, 1), (90, 66, 98), (105, 116, 203), (106, 161, 253), (81, 205, 236), (76, 237, 191),
                   (132, 253, 135), (191, 251, 95), (233, 226, 96), (254, 189, 93), (248, 137, 71), (224, 95, 56),
                   (182, 66, 52)]
        invertedColors = []
        for i in range(len(colours)):
            invertedColors.append((255 - colours[i][0], 255 - colours[i][1], 255 - colours[i][2]))

        # Find contours (blobs) of binary image
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        # remove all contours whose area is smaller than 5000 pixels
        sortedContours = [contour for contour in contours if cv2.contourArea(contour) > 5000]
        sortedContours = sorted(sortedContours, key=cv2.contourArea, reverse=True)

        y = image.shape[0]
        x = image.shape[1]
        blankImage = np.zeros((y, x), np.uint8)
        contoursDrawn = cv2.drawContours(blankImage, sortedContours, -1, 255, -1)
        blobsData, positions, separateContours = self.blobProperties(sortedContours, y, x)

        imagePlotAll = np.zeros((y, x), np.uint8)
        imagePlotAll = cv2.cvtColor(imagePlotAll, cv2.COLOR_GRAY2RGB)
        for i, fishID in enumerate(blobsData):
            imagePlot = np.zeros((y, x), np.uint8)
            imagePlot = cv2.cvtColor(imagePlot, cv2.COLOR_GRAY2RGB)

            averagePoint = positions[i][4]
            extremePointLeft = positions[i][0]
            extremePointRight = positions[i][1]
            extremePointTop = positions[i][2]
            extremePointBottom = positions[i][3]
            extremePointList = [extremePointLeft, extremePointRight, extremePointTop, extremePointBottom]

            originalImage = cv2.rectangle(imageData.img, [extremePointLeft[0], extremePointTop[1]],
                                          [extremePointRight[0], extremePointBottom[1]], colours[i], 2)

            cv2.drawContours(imagePlot, separateContours[i], -1, colours[i], -1)  # , colours[i], thickness=cv2.FILLED)

            lineColor = [round(255 / 2), round(255 / 2), round(255 / 2)]

            # print("Drawing average point: ", averagePoint)

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
                lenghts[lenghts.index(sorted(lenghts, reverse=True)[1])] = 0
                extremePoint2Index = lenghts.index(sorted(lenghts, reverse=True)[1])
                extremePoint2 = extremePointList[extremePoint2Index]
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

            # Label lenght of fish
            cv2.putText(imagePlot, str(round(convertedLenght, 1)), (averagePoint[0], averagePoint[1] + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(imagePlot, str(round(convertedLenght, 1)), (averagePoint[0], averagePoint[1] + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (255, 255, 255), 1, cv2.LINE_AA)

            # Label blobs
            fishText = "Fish" + str(fishID)
            #fishText = str(round(blobsData[i][1]))
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
            extremePoint1List.append(extremePoint1)
            extremePoint2List.append(extremePoint2)
            imagePlotAll = cv2.add(imagePlotAll, imagePlot)

        # print(fishLenght)
        #self.showImage([imagePlotAll])
        return fishLenght, fishOrientation, imagePlotAll, originalImage, averagePoints, separateContours, extremePoint1List, extremePoint2List
