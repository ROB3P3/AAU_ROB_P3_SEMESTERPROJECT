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
        areas = []
        finalBlobs = self.imageData.seperatedThresholdedImage
        contoursFinal = np.zeros((y, x), np.uint8)
        fishID = 1

        # Goes through every blob
        for contour in contours:
            averagePoint = []

            # Get all pixel positions in contour to calculate average point
            extracted = np.zeros((y, x), np.uint8)
            extracted = cv2.drawContours(extracted, [contour], -1, 255, -1)

            extractedOriginal = self.imageOriginal.copy()
            # Add the contour to the image copy
            extractedOriginal = cv2.drawContours(extractedOriginal, [contour], -1, (0, 0, 255), 2)

            # Crop the image to the blob
            yPixelValues, xPixelValues = np.nonzero(extracted)
            xMin = min(xPixelValues)
            xMax = max(xPixelValues)
            yMin = min(yPixelValues)
            yMax = max(yPixelValues)
            print("Normal: ", xMin, xMax, yMin, yMax)
            extractedCropped = extracted.copy()[yMin:yMax, xMin:xMax]

            # Add 50 pixels to each side of the cropped image to make sure the fish is not cut off
            extractedCropped = cv2.copyMakeBorder(extractedCropped, 25, 25, 25, 25, cv2.BORDER_CONSTANT, value=0)
            extractedOriginalCropped = extractedOriginal.copy()[yMin-25:yMax+25, xMin-25:xMax+25]



            # write the image to file
            cv2.imwrite("C:/P3OutData/Example/Size/Convex/{}Normal.png".format(fishID), extractedCropped)
            cv2.imwrite("C:/P3OutData/Example/Size/Convex/{}RGBNormal.png".format(fishID), extractedOriginalCropped)
            #self.showImage([extracted, extractedCropped])

            #if x == 1920:
            #    self.showImage([extracted])

            # Make a copy of the blobs in RGB to use as a comparison image
            blobsRGB = extracted.copy()
            blobsRGB = cv2.cvtColor(blobsRGB, cv2.COLOR_GRAY2RGB)

            # Make a copy of the image to draw on
            boundedContours = extracted.copy()
            boundedContoursPoints = extracted.copy()

            # Find the convex hull of the contour, withouth returning the points so that it can be used to find the convexity defects
            hull = cv2.convexHull(contour, returnPoints=False)

            # Find the convexity defects of the contour and use them to draw the convex hull
            try:
                defects = cv2.convexityDefects(contour, hull)
            except cv2.error as error:
                print("In picture: ", self.imageData.imagePath)
                print("Error in convexity defects:")
                print(error)
                continue

            for i in range(defects.shape[0]):
                # Get the start, end, and far points of the convexity defect
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])


                # Calculate the lenght of the line from the start to the end point
                lenght = math.sqrt((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2)


                cv2.line(boundedContours, start, far, 255, 2)
                cv2.line(boundedContours, end, far, 255, 2)

            # Extract the new bounded contour
            boundedContours = cv2.findContours(boundedContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

            extractedBounded = np.zeros((y, x), np.uint8)
            extractedBounded = cv2.drawContours(extractedBounded, [boundedContours[0]], -1, 255, -1)
            boundedOriginal = self.imageOriginal.copy()
            boundedOriginal = cv2.drawContours(boundedOriginal, [boundedContours[0]], -1, (0, 0, 255), 2)


            yPixelValues, xPixelValues = np.nonzero(extractedBounded)
            xMin = min(xPixelValues)
            xMax = max(xPixelValues)
            yMin = min(yPixelValues)
            yMax = max(yPixelValues)
            print("Bounded: ", xMin, xMax, yMin, yMax)
            extractedBoundedCropped = extractedBounded[yMin:yMax, xMin:xMax]

            # Add black pixels to the sides of the cropped image so it is the same size as the other cropped image
            print("Shape: ", extractedCropped.shape, extractedBoundedCropped.shape)
            xDifference = round((extractedCropped.shape[1] - extractedBoundedCropped.shape[1])/2)
            yDifference = round((extractedCropped.shape[0] - extractedBoundedCropped.shape[0])/2)
            extractedBoundedCropped = cv2.copyMakeBorder(extractedBoundedCropped, yDifference, yDifference, xDifference, xDifference, cv2.BORDER_CONSTANT, value=0)
            boundedOriginalCropped = boundedOriginal[yMin-yDifference:yMax+yDifference, xMin-xDifference:xMax+xDifference]


            cv2.imwrite("C:/P3OutData/Example/Size/Convex/{}Convex.png".format(fishID), extractedBoundedCropped)
            cv2.imwrite("C:/P3OutData/Example/Size/Convex/{}RGBConvex.png".format(fishID), boundedOriginalCropped)



            #self.showImage([extractedCropped, extractedBoundedCropped, extractedBoundedPointsCropped])

            # Get all pixel positions in contour to calculate average point
            yPixelValues, xPixelValues = np.nonzero(extractedBounded)
            # print(yPixelValues, xPixelValues)
            # self.showImage([extractedBounded])

            # Add each bounded contour to a list so they can be accessed separately
            separateContours.append(boundedContours)

            # Get area of bounded contour
            area = cv2.contourArea(boundedContours[0])
            areas.append(area)
            properties.append(fishID)

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
            cv2.drawContours(contoursFinal, boundedContours, -1, 255, -1)
        #if x == 1920:
        #    self.showImage([contoursFinal])
        return properties, positions, separateContours, areas

    def findSize(self, imageData):  # image, imageOriginal): #
        """Function to find the area and lenght of a fish(blob). image -> binary"""
        self.imageData = imageData
        image = imageData.calibratedThresholdedImage
        imageBlobUncalibrated = imageData.seperatedThresholdedImage
        imageOriginal = imageData.img.copy()
        self.imageOriginal = imageOriginal.copy()

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
        contoursUncalibrated = cv2.findContours(imageBlobUncalibrated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        # remove all contours whose area is smaller than 5000 pixels in area
        sortedContours = [contour for contour in contours if cv2.contourArea(contour) > 5000]
        sortedContoursUncalibrated = [contour for contour in contoursUncalibrated if cv2.contourArea(contour) > 5000]


        y = image.shape[0]
        x = image.shape[1]
        blankImage = np.zeros((y, x), np.uint8)
        contoursDrawn = cv2.drawContours(blankImage, sortedContours, -1, 255, -1)

        # erode and dilate to make contours monotonous for convex defects
        image = cv2.erode(contoursDrawn, np.ones((3, 3), np.uint8), iterations=1)
        image = cv2.dilate(image, np.ones((3, 3), np.uint8), iterations=1)
        #cv2.imshow("contoursDrawn", contoursDrawn)



        yUncalibrated = imageOriginal.shape[0]
        xUncalibrated = imageOriginal.shape[1]
        blankImageUncalibrated = np.zeros((yUncalibrated, xUncalibrated), np.uint8)
        contoursDrawnUncalibrated = cv2.drawContours(blankImageUncalibrated, sortedContoursUncalibrated, -1, 255, -1)
        imageBlobUncalibrated = cv2.erode(contoursDrawnUncalibrated, np.ones((3, 3), np.uint8), iterations=1)
        imageBlobUncalibrated = cv2.dilate(imageBlobUncalibrated, np.ones((3, 3), np.uint8), iterations=1)
        #cv2.imshow("contoursDrawnUncalibrated", contoursDrawnUncalibrated)
        #cv2.waitKey(0)

        # Find contours (blobs) of binary image
        contours = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        # remove all contours whose area is smaller than 5000 pixels
        sortedContours = [contour for contour in contours if cv2.contourArea(contour) > 5000]
        #sortedContours = sorted(sortedContours, key=cv2.contourArea, reverse=True)
        blobsData, positions, separateContours, fishAreas = self.blobProperties(sortedContours, y, x)

        contoursUncalibrated = cv2.findContours(imageBlobUncalibrated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        sortedContoursUncalibrated = [contour for contour in contoursUncalibrated if cv2.contourArea(contour) > 5000]
        #sortedContoursUncalibrated = sorted(sortedContoursUncalibrated, key=cv2.contourArea, reverse=True)
        blobsDataUncalibrated, positionsUncalibrated, separateContoursUncalibrated, fishAreasUncalibrated = self.blobProperties(
            sortedContoursUncalibrated, yUncalibrated, xUncalibrated)

        imagePlotUncalibrated = np.zeros((yUncalibrated, xUncalibrated), np.uint8)
        imagePlotUncalibrated = cv2.cvtColor(imagePlotUncalibrated, cv2.COLOR_GRAY2RGB)

        for i in range(len(blobsDataUncalibrated)):
            # Points for the uncalibrated blob image
            averagePointUncalibrated = positionsUncalibrated[i][4]
            extremePointLeftUncalibrated = positionsUncalibrated[i][0]
            extremePointRightUncalibrated = positionsUncalibrated[i][1]
            extremePointTopUncalibrated = positionsUncalibrated[i][2]
            extremePointBottomUncalibrated = positionsUncalibrated[i][3]
            extremePointListUncalibrated = [extremePointLeftUncalibrated, extremePointRightUncalibrated,
                                            extremePointTopUncalibrated, extremePointBottomUncalibrated]

            originalImage = cv2.rectangle(imageOriginal,
                                          [extremePointLeftUncalibrated[0], extremePointTopUncalibrated[1]],
                                          [extremePointRightUncalibrated[0], extremePointBottomUncalibrated[1]],
                                          colours[i], 2)
            cv2.drawContours(imagePlotUncalibrated, separateContoursUncalibrated[i], -1, colours[i], -1)

            # Label blobs
            fishText = "Fish" + str(i+1)
            # fishText = str(round(blobsData[i]))
            cv2.putText(imagePlotUncalibrated, fishText, averagePointUncalibrated, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(imagePlotUncalibrated, fishText, averagePointUncalibrated, cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                        invertedColors[i], 1, cv2.LINE_AA)


        # self.showImage([blankUncalibrated])

        imagePlotAll = np.zeros((y, x), np.uint8)
        imagePlotAll = cv2.cvtColor(imagePlotAll, cv2.COLOR_GRAY2RGB)
        for i, fishID in enumerate(blobsData):
            imagePlot = np.zeros((y, x), np.uint8)
            imagePlot = cv2.cvtColor(imagePlot, cv2.COLOR_GRAY2RGB)

            # Points for the calibrated blob image
            averagePoint = positions[i][4]
            extremePointLeft = positions[i][0]
            extremePointRight = positions[i][1]
            extremePointTop = positions[i][2]
            extremePointBottom = positions[i][3]
            extremePointList = [extremePointLeft, extremePointRight, extremePointTop, extremePointBottom]

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
            # fishText = str(round(blobsData[i]))
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
        # self.showImage([imagePlotAll])
        # Get amount of files in C:/FishProject/group_4/output/Size/
        # numberOfFiles = len(glob.glob("C:/FishProject/group_4/output/Size/*.png"))+1
        # imagePath = imageData.imagePath
        # name = imagePath.rsplit('\\', 1)[-1]
        # cv2.imwrite("C:/FishProject/group_4/output/Size/Annontaded{}".format(name), imagePlotAll)
        return fishLenght, fishOrientation, imagePlotAll, originalImage, averagePoints, separateContoursUncalibrated, extremePoint1List, extremePoint2List, fishAreas, imagePlotUncalibrated
