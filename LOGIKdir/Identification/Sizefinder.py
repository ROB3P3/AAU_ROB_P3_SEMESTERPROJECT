import cv2
import numpy as np
import math

imageBinary = cv2.imread(r"DATAdir/RGB/tiff/00016binary.tiff", cv2.IMREAD_UNCHANGED)


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
        if area > 10000:
            # Finds the center and radius of the minimum enclosing circle
            (xc, yc), radius = cv2.minEnclosingCircle(contourPixels)
            # Pixel points have to be round numbers
            circleCenter = (round(xc), round(yc))

            # Fit an ellipce around the blob. Get
            ellipse = cv2.fitEllipse(contourPixels)
            ellipsePoints = ((round(ellipse[0][0]),round(ellipse[0][1])), (round(ellipse[1][0]),round(ellipse[1][1])))
            ellipseAngle = ellipse[2]
            print("eCenter: ", ellipsePoints, "angle: ", ellipseAngle)
            add = fishID, circleCenter, radius, ellipsePoints, ellipseAngle

            """add = fishID, area, round(perimeter, 1), convexity, round(aspect_ratio, 3), round(extent, 3), w, h, round(
                hull_area, 1), round(angle, 1), x1, y1, x2, y2, round(radius, 6), xa, ya, xc, yc, xf[0], yf[
                0], rect, ellipse, vx[0], vy[0], lefty, righty"""
            properties.append(add)

            for pixel in contourPixels:
                pixelPositionX.append(pixel[0][1])
                pixelPositionY.append(pixel[0][0])

            averagePointY = round(sum(pixelPositionX) / len(pixelPositionX))
            averagePointX = round(sum(pixelPositionY) / len(pixelPositionY))

            averagePoint.append([averagePointX, averagePointY])

            minPositionX = pixelPositionX.index(min(pixelPositionX))
            maxPositionX = pixelPositionX.index(max(pixelPositionX))
            minPositionY = pixelPositionY.index(min(pixelPositionY))
            maxPositionY = pixelPositionY.index(max(pixelPositionY))

            positions.append([contourPixels[minPositionX], contourPixels[maxPositionX], contourPixels[minPositionY],
                              contourPixels[maxPositionY], averagePoint])

            fishID += 1
    return properties, positions


def findSize(image):
    """Function to find the area and lenght of a fish(blob)"""

    fishLenght = []
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
        radius = round(data[2])
        ellipsePoints = data[3]
        ellipseAngle = round(data[4])

        averagePoint = positions[i][4][0]
        mininumPointX = positions[i][0][0]
        maximumPointX = positions[i][1][0]
        mininumPointY = positions[i][2][0]
        maximumPointY = positions[i][3][0]

        print("ellipse: ", ellipsePoints[0], ellipsePoints[1], ellipseAngle)

        ellipsePointsCorrected = (round(ellipsePoints[0][0]*math.cos(ellipseAngle*math.pi/180)), round(ellipsePoints[0][1]*math.sin(ellipseAngle*math.pi/180)))

        cv2.drawContours(imagePlot, [sortedContours[i]], -1, colours[i], -1)  # , colours[i], thickness=cv2.FILLED)

        cv2.line(imagePlot, ellipsePoints[0], ellipsePointsCorrected, (230, 230, 230), 2)

        directionPoint = (round(math.cos(ellipseAngle) * 1000 + averagePoint[0]), -round(math.sin(ellipseAngle) * 1000+ averagePoint[1]))

        print(directionPoint)

        cv2.line(imagePlot, averagePoint, directionPoint, (255, 255, 255), 2)



        # Bounding boxes
        # Rotated rectangle
        # rect = blobsData[i][21]
        # box = cv2.boxPoints(rect)
        # box = np.intp(box)

        # Mimimum enclosing circle
        # centre = (int(blobsData[i][17]), int(blobsData[i][18]))
        # radius = int(blobsData[i][14])

        # plotting
        # rows, cols = image.shape[:2]
        # cv2.rectangle(imagePlot, (data[10], data[11]), (data[12], data[13]), colours[1], 2)  # Bounding rectangle
        # cv2.drawContours(imagePlot, [box], 0, colours[4], 2)  # Rotated rectangle
        #cv2.circle(imagePlot, centre, radius, invertedColors[i], 2)  # Minimum Enclosing Circle
        cv2.ellipse(imagePlot, (ellipsePoints[0], ellipsePoints[1], ellipseAngle), invertedColors[i], 2)  # Fitted ellipse

        break



        lineColor = singleRGBcolor(255)

        cv2.line(imagePlot, averagePoint, mininumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointX, lineColor, 2)
        cv2.line(imagePlot, averagePoint, mininumPointY, lineColor, 2)
        cv2.line(imagePlot, averagePoint, maximumPointY, lineColor, 2)

        lenghtCircle = radius * 2
        print("Circle lenght: ", lenghtCircle)

        lenght2MinX = math.sqrt((mininumPointX[0] - averagePoint[0]) ** 2 + (mininumPointX[1] - averagePoint[1]) ** 2)
        lenght2MaxX = math.sqrt((maximumPointX[0] - averagePoint[0]) ** 2 + (maximumPointX[1] - averagePoint[1]) ** 2)
        lenght2MinY = math.sqrt((mininumPointY[0] - averagePoint[0]) ** 2 + (mininumPointY[1] - averagePoint[1]) ** 2)
        lenght2MaxY = math.sqrt((maximumPointY[0] - averagePoint[0]) ** 2 + (maximumPointY[1] - averagePoint[1]) ** 2)

        lenghts = [lenght2MinX, lenght2MaxX, lenght2MinY, lenght2MaxY]
        totalLenght = sum(sorted(lenghts)[2:])
        print("Totallenght: ", totalLenght)

        cv2.putText(imagePlot, str(round(totalLenght)), averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, str(round(totalLenght)), averagePoint, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)


        fishText = "Fish" + str(fishID)
        cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(imagePlot, fishText, centre, cv2.FONT_HERSHEY_SIMPLEX, 1,
                    invertedColors[i], 2, cv2.LINE_AA)

        fishLenght.append(totalLenght)

        if i == 40:
            """print("Center: ", centre)
            print("Average: ", positions[i][4][0])
            print("minPosX: ", positions[i][0][0])
            print("maxPosX: ", positions[i][1][0])
            print("minPosY: ", positions[i][2][0])
            print("maxPosY: ", positions[i][3][0])"""
            break

    print(fishLenght)
    showImage(imagePlot)


findSize(imageBinary)
