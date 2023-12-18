import cv2
import numpy as np
import os


class GrippingPoints:
    def __init__(self) -> None:
        print("GrippingPoints initialized")

    def applyZValues(self, imageData):
        averagePoints = imageData.averagePoints
        grippingPoints = imageData.fishGrippingPoints
        imageZ = imageData.imageWithZValues

        newAveragePoints = []
        newGrippingPoints = []
        for i, point in enumerate(averagePoints):
            zCoord = (imageZ[point[1]][point[0]][0] - 10.8) / 2 if imageZ[point[1]][point[0]][0] > 10.8 else 0
            newAveragePoints.append([point[0], point[1], zCoord])
            newGrippingPoints.append([[grippingPoints[i][0][0], grippingPoints[i][0][1], zCoord],
                                      [grippingPoints[i][1][0], grippingPoints[i][1][1], zCoord]])

        # add this into data.py
        return newAveragePoints, newGrippingPoints

    def calcGrippingPoints(self, imageData):
        """Calculate the grasping points of the fish"""
        # Change to use the image with new blobs from Sizefinder
        image = imageData.calibratedNotAnnotatedImage
        gripImage = image.copy()
        extremes1 = imageData.extremePointList1
        extremes2 = imageData.extremePointList2
        centerpoints = imageData.averagePoints
        grippingPoints = []
        fishWidths = []

        # Loop through all the fish
        for i in range(len(extremes1)):
            # Calculate the vector between the extreme points
            vector = np.asarray([extremes2[i][0] - extremes1[i][0], extremes2[i][1] - extremes1[i][1]])
            # Calulate the perpendicular vector
            perpendicularVector = np.array([-vector[1], vector[0]])
            perpendicularLength = np.linalg.norm(perpendicularVector)

            gripImage = cv2.line(gripImage, (extremes1[i][0], extremes1[i][1]), (extremes2[i][0], extremes2[i][1]),
                                 (0, 0, 255), 2)
            gripImage = cv2.line(gripImage, (extremes1[i][0], extremes1[i][1]),
                                 (extremes1[i][0] + perpendicularVector[0], extremes1[i][1] + perpendicularVector[1]),
                                 (0, 255, 0), 2)

            # Normalize the perpendicular vector for 2 directions
            posNormalizedVector = perpendicularVector / perpendicularLength
            negNormalizedVector = perpendicularVector / perpendicularLength

            # Find the current pixel of the perpendicular vector based in the centerpoint
            positivePixel = [round(centerpoints[i][0] + posNormalizedVector[0]),
                             round(centerpoints[i][1] + posNormalizedVector[1])]
            negativePixel = [round(centerpoints[i][0] + negNormalizedVector[0]),
                             round(centerpoints[i][1] + negNormalizedVector[1])]

            # Increase the length of the perpendicular vector until it hits black in both directions
            # When the vector hits black, the vector has hit the edge of the fish, and this pixel is the gripping point
            vectorIncCounter = 1
            try:
                while np.sum(image[positivePixel[1]][positivePixel[0]]) != 0:
                    posNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                    positivePixel = [round(centerpoints[i][0] + posNormalizedVector[0]),
                                     round(centerpoints[i][1] + posNormalizedVector[1])]
                    vectorIncCounter += 1
            except:
                posNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                positivePixel = [round(centerpoints[i][0] + posNormalizedVector[0]),
                                 round(centerpoints[i][1] + posNormalizedVector[1])]

            vectorIncCounter = -1
            try:
                while np.sum(image[negativePixel[1]][negativePixel[0]]) != 0:
                    negNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                    negativePixel = [round(centerpoints[i][0] + negNormalizedVector[0]),
                                     round(centerpoints[i][1] + negNormalizedVector[1])]
                    vectorIncCounter -= 1
            except:
                negNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                negativePixel = [round(centerpoints[i][0] + negNormalizedVector[0]),
                                 round(centerpoints[i][1] + negNormalizedVector[1])]

            # Calculate the width based on the vector between the gripping points
            grippingPoint = [positivePixel, negativePixel]
            grippingPointVector = np.asarray(grippingPoint[0]) - np.asarray(grippingPoint[1])
            width = np.linalg.norm(grippingPointVector)

            gripImage = cv2.line(gripImage, (positivePixel[0], positivePixel[1]), (negativePixel[0], negativePixel[1]),
                                 (255, 255, 0), 2)

            grippingPoints.append(grippingPoint)
            fishWidths.append(width)


        return grippingPoints, fishWidths, gripImage
