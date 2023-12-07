import cv2
import numpy as np


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
            newAveragePoints.append([point[0], point[1], round(imageZ[point[1]][point[0]][0])])
            newGrippingPoints.append(
                [[grippingPoints[i][0][0], grippingPoints[i][0][1], round(imageZ[point[1]][point[0]][0])],
                 [grippingPoints[i][1][0], grippingPoints[i][1][1], round(imageZ[point[1]][point[0]][0])]])

        # add this into data.py
        return newAveragePoints, newGrippingPoints

    def calcGrippingPoints(self, imageData):
        """Calculate the grasping points of the fish"""
        # Change to use the image with new blobs from Sizefinder
        image = imageData.annotatedImage
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
            while np.sum(image[positivePixel[1]][positivePixel[0]]) != 0:
                posNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                positivePixel = [round(centerpoints[i][0] + posNormalizedVector[0]),
                                 round(centerpoints[i][1] + posNormalizedVector[1])]
                vectorIncCounter += 1

            vectorIncCounter = -1
            while np.sum(image[negativePixel[1]][negativePixel[0]]) != 0:
                negNormalizedVector = (perpendicularVector / perpendicularLength) * vectorIncCounter
                negativePixel = [round(centerpoints[i][0] + negNormalizedVector[0]),
                                 round(centerpoints[i][1] + negNormalizedVector[1])]
                vectorIncCounter -= 1

            # Calculate the width based on the vector between the gripping points
            grippingPoint = [positivePixel, negativePixel]
            grippingPointVector = np.asarray(grippingPoint[0]) - np.asarray(grippingPoint[1])
            width = np.linalg.norm(grippingPointVector)

            grippingPoints.append(grippingPoint)
            fishWidths.append(round(width))

        return grippingPoints, fishWidths
