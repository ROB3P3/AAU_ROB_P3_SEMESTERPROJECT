import numpy as np
import cv2
import glob
import os


def removeSides(image):
    """Function to remove the sides of the PNG images"""
    # manually found the x-coordinates for the sides on the top and bottom
    xLeftTop = 656
    xLeftBot = 677
    xRightTop = 1824
    xRightBot = 1870

    """for y, row in enumerate(image):
        for x, col in enumerate(row):
            # since the image is crooked, the sides are removed by scaling the difference in the x-coordinates with the y-coordinate
            if x <= (xLeftTop + math.floor((((xLeftBot - xLeftTop) / 1080) * y))) or x >= (
                    xRightTop + math.floor((((xRightBot - xRightTop) / 1080) * y))):
                image[y][x] = 0"""
    image = image[0:1080, xLeftTop:xRightBot]
    return image


def showImage(images):
    """Function to show an array of images until 0 is pressed"""
    for i, image in enumerate(images): cv2.imshow("Image"+str(i+1), image)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)


def getImageCalibration(group):
    """Gets the values required for undistorting and image based on a checkerboard."""
    # termination criteria
    # Define the dimensions of checkerboard
    CHECKERBOARD = (6, 9)

    # stop the iteration when specified
    # accuracy, epsilon, is reached or
    # specified number of iterations are completed.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Vector for 3D points in real world space
    points3D = []

    # Vector for 2D points in image plane.
    points2D = []

    # Prepares 3D points real world coordinates like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0).
    objectPoints3D = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objectPoints3D[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

    # Extracting path of individual images stored in a given directory.
    images = glob.glob(r'DATAdir\RGB\Group{}\CalibrationPNG\*.png'.format(group))

    for fileName in images:
        print(fileName)
        image = cv2.imread(fileName, cv2.IMREAD_UNCHANGED)
        #showImage([image])
        image = removeSides(image)
        grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        # If desired number of corners are
        # found in the image then retval = true
        retval, corners = cv2.findChessboardCorners(grayColor, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH
                                                    + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

        # If desired number of corners can be detected then,
        # refine the pixel coordinates and display
        # them on the images of checkerboard
        if retval == True:
            points3D.append(objectPoints3D)

            # Refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), criteria)

            points2D.append(corners2)

            # Draw and display the corners
            imageDrawn = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, retval)
            #showImage([imageDrawn])
        else:
            print("Can't find anything: ", fileName)

    # Perform camera calibration by passing the value of above found out 3D points (points3D)
    # and its corresponding pixel coordinates of the detected corners (points2D)
    print("Calculating camera calibration values...")
    retval, matrix, distortion, rotationVector, translationVector = cv2.calibrateCamera(points3D, points2D,
                                                                                        grayColor.shape[::-1], None,
                                                                                        None)

    # Displaying required output
    print(" Camera matrix:")
    print(matrix)

    print("\n Distortion coefficient:")
    print(distortion)

    print("\n Rotation Vectors:")
    print(rotationVector)

    print("\n Translation Vectors:")
    print(translationVector)

    # Get new camera matrix
    height, width = image.shape[:2]
    print("h+w: ", height, width)
    newCameraMatrix, regionsOfInterest = cv2.getOptimalNewCameraMatrix(matrix, distortion, (width, height), 1,
                                                                       (width, height))

    return [retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest]


def calibrateImage(correctionValues, group):
    images = glob.glob(r'DATAdir\RGB\Group{}\CalibrationPNG\*.png'.format(group))
    retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest = correctionValues

    for fileName in images:
        print("writing calibrated image for:", fileName.rsplit('\\', 1)[-1])
        image = cv2.imread(fileName)
        image = removeSides(image)
        imageUndistorted = cv2.undistort(image, matrix, distortion, None, newCameraMatrix)

        # Crop image to region of interest
        x, y, width, height = regionsOfInterest
        imageUndistorted = imageUndistorted[y:y + height, x:x + width]

        #showImage([imageUndistorted])
        newFileName = r"DATAdir/RGB/Group{}/CalibratedPNG/".format(group) + "calibrated" + fileName.rsplit('\\', 1)[-1]
        print(newFileName)
        cv2.imwrite(newFileName, imageUndistorted)


if __name__ == "__main__":
    group = 9
    calibration = getImageCalibration(group)
    calibrateImage(calibration, group)
