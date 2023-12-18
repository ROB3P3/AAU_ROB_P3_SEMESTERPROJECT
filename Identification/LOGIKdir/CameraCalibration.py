import numpy as np
import cv2
import glob
import os
# from LOGIKdir.AutoCrop import Cropper as AutoCrop
from LOGIKdir.AutoCrop import Cropper as AutoCrop
from LOGIKdir.Sizefinder import SizeFinder


class ImageCalibrator:
    def __init__(self) -> None:
        print("ImageCalibrator initialized:")

    def clearDirectory(self, path):
        """Delete all files in the given folder"""
        print("Deleting files in: ", path)
        files = glob.glob(path)
        for file in files:
            # print("Deleted ", file)
            os.remove(file)

    def showImage(self, images):
        """Function to show an array of images until 0 is pressed"""
        for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
        while True:
            k = cv2.waitKey(0) & 0xFF
            if k == 48:
                break
            print(k)

    def WarpPerspective(self, image, fileName=None):
        """Warp the perspective of a 1920x1080 PNG in group 9 image to help account for the angle of the camera.
        Takes a PNG image and warps it to a 1080x1080 pixel image containing only the conveyor."""
        AutoCropper = AutoCrop()
        AutoCropper.setImage(image)
        minX = AutoCropper.crop()
        leftX1 = minX + 67
        leftX2 = minX + 70
        rightX1 = minX + 1235
        rightX2 = minX + 1270

        # Points in the orignal image indicating where to warp perspective to.
        # Change to use automatic detection of points.
        orignalPoints = np.float32([[leftX1, 0], [leftX2, 1080], [rightX1, 0], [rightX2, 1080]])
        # What the originalPoints new values should be in the perspective warped image
        newPoints = np.float32([[0, 0], [0, 1080], [1080, 0], [1080, 1080]])
        # Warp all checkerboard images and put them in their own folder.
        warpMatrix = cv2.getPerspectiveTransform(orignalPoints, newPoints)
        # Use the values from above to warp the image to a 1080x1080 pixel image.
        return warpMatrix

    def getImageCalibration(self, calibrationPath):
        """Gets the values required for undistorting an image based on checkerboards in multiple images."""
        # termination criteria
        # Define the dimensions of checkerboard
        CHECKERBOARD = (9, 6)

        # The criteria for when to stop iterating, determined either by reaching a certain accuracy (like 0.001) or
        # when a certain number of iterations have been performed (like 30)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Vector for 3D points in real world space
        points3D = []

        # Vector for 2D points in image plane.
        points2D = []

        # Prepares 3D points real world coordinates like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0).
        objectPoints3D = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
        objectPoints3D[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

        print("Finding checkerboards in images...", calibrationPath)
        for fileName in calibrationPath:
            name = fileName.rsplit('\\', 1)[-1]
            image = cv2.imread(fileName)

            # Warp perspective of board
            warpMatrix = self.WarpPerspective(image, name)
            image = cv2.warpPerspective(image, warpMatrix, (1080, 1080))

            print("Finding Checkerboards for {}".format(name))
            # Convert to greyscale
            grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            # If desired number of corners are found in the image then retval = true
            retval, corners = cv2.findChessboardCorners(grayColor, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH
                                                        + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

            # If desired number of corners are detected, refine the pixel coordinates and display them .
            if retval == True:
                points3D.append(objectPoints3D)

                # Refining pixel coordinates for given 2d points.
                corners2 = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), criteria)

                points2D.append(corners2)

                # Draw and display the corners
                # imageDrawn = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, retval)
                # showImage([imageDrawn])
            else:
                print("Can't find enough corners in {}.".format(name))

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
        newCameraMatrix, regionsOfInterest = cv2.getOptimalNewCameraMatrix(matrix, distortion, (width, height), 1,
                                                                           (width, height))

        return [retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest]

    def calibrateImage(self, imageRGB, imageBlobs, calibrationValues):
        """Apllies the calibration values found in getImageCalibration() to the images in the group"""

        retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest = calibrationValues
        # Get warp matrix to perspective transform the images.
        warpMatrix = self.WarpPerspective(imageRGB)
        # Warp the images using the warp matrix.
        imageRGB = cv2.warpPerspective(imageRGB, warpMatrix, (1080, 1080))
        imageBlobsWarped = cv2.warpPerspective(imageBlobs, warpMatrix, (1080, 1080))

        # Calibrate the warped image.
        # print("Calibrating {} image {}.".format(imagePath.rsplit("/", 1)[-2], name))
        imageRGBUndistorted = cv2.undistort(imageRGB, matrix, distortion, None, newCameraMatrix)
        imageBlobsUndistorted = cv2.undistort(imageBlobsWarped, matrix, distortion, None, newCameraMatrix)

        # Crop image to region of interest.
        x, y, width, height = regionsOfInterest
        imageRGBUndistorted = imageRGBUndistorted[y:y + height, x:x + width]
        imageBlobsUndistorted = imageBlobsUndistorted[y:y + height, x:x + width]
        ret, imageBlobsUndistorted = cv2.threshold(imageBlobsUndistorted, 200, 255, 0)

        return [imageRGBUndistorted, imageBlobsUndistorted]
