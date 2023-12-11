import numpy as np
import cv2
import glob
import os
#from LOGIKdir.AutoCrop import Cropper as AutoCrop
from Identification.LOGIKdir.AutoCrop import Cropper as AutoCrop
from Identification.LOGIKdir.Sizefinder import SizeFinder


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
        # print("Warping perspective of {}.".format(fileName))
        warpMatrix = cv2.getPerspectiveTransform(orignalPoints, newPoints)
        # Use the values from above to warp the image to a 1080x1080 pixel image.
        return warpMatrix

    def getImageCalibration(self, calibrationPath):
        """Gets the values required for undistorting an image based on checkerboards in multiple images."""
        # termination criteria
        # Define the dimensions of checkerboard
        boardShape = (9, 6)

        #
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        #criteria = (cv2.TERM_CRITERIA_MAX_ITER, 30)

        # Vector for 3D points in real world space
        points3D = []

        # Vector for 2D points in image plane.
        points2D = []

        # Prepares 3D points real world coordinates like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0).
        objectPoints3D = np.zeros((boardShape[0] * boardShape[1], 3), np.float32)
        objectPoints3D[:, :2] = np.mgrid[0:boardShape[0], 0:boardShape[1]].T.reshape(-1, 2)

        print("Preparing objectPoints3D: ", len(objectPoints3D))

        print("Finding checkerboards in images...", calibrationPath)
        for i, fileName in enumerate(calibrationPath):
            name = fileName.rsplit('\\', 1)[-1]
            name = name.rsplit('.', 1)[0]
            image = cv2.imread(fileName)

            if i == 0:
                # Warp perspective of board
                warpMatrix = self.WarpPerspective(image, name)
            image = cv2.warpPerspective(image, warpMatrix, (1080, 1080))

            print("Finding Checkerboards for {}".format(name))
            # Convert to greyscale
            grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #grayColor = image


            # Find the chess board corners
            # If desired number of corners are found in the image then retval = true
            retval, corners = cv2.findChessboardCorners(grayColor, boardShape, cv2.CALIB_CB_ADAPTIVE_THRESH
                                                        + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

            # If desired number of corners are detected, refine the pixel coordinates and display them .
            if retval == True:
                points3D.append(objectPoints3D)
                #print("Appended points3D: ", points3D)

                # Refining pixel coordinates for given 2d points.
                corners2 = cv2.cornerSubPix(grayColor, corners, (11, 11), (-1, -1), criteria)

                points2D.append(corners2)

                # Draw and display the corners
                imageDrawn = cv2.drawChessboardCorners(image, boardShape, corners2, retval)
                #self.showImage([imageDrawn])
                newFileName = "C:/P3OutData/Example/Checkerboard/{}Uncalibrated.png".format(name)
                print("Writing to: ", newFileName)
                cv2.imwrite(newFileName, imageDrawn)

            else:
                print("Can't find enough corners in {}.".format(name))
                # showImage([image])

        print("After objectPoints3D: ", len(points3D), points3D)

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

        meanError = 0
        for i in range(len(points3D)):
            imgpoints2, _ = cv2.projectPoints(points3D[i], rotationVector[i], translationVector[i], matrix, distortion)
            error = cv2.norm(points2D[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            meanError += error
        print("total error: {}".format(meanError / len(points3D)))

        return [retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest]

    def calibrateImage(self, imageRGB, imageBlobs, calibrationValues):
        """Apllies the calibration values found in getImageCalibration() to the images in the group"""
        # Clear output folder to ensure only the newest files.
        # outputPathFish = outputPath + "WarpedCalibratedFish/{}"
        # outputPathCalibration = outputPath + "WarpedCalibratedCheckerboard/{}"
        # Clear both output folders
        # clearDirectory(outputPathFish.format("*"))
        # clearDirectory(outputPathCalibration.format("*"))

        retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest = calibrationValues
        # If the shape of the image is 1920x1080, warp the perspective to 1080x1080
        if imageRGB.shape[0] == 1920 and imageRGB.shape[1] == 1080:
            # Get warp matrix to perspective transform the images.
            warpMatrix = self.WarpPerspective(imageRGB)
            imageRGB = cv2.warpPerspective(imageRGB, warpMatrix, (1080, 1080))
            imageBlobsWarped = cv2.warpPerspective(imageBlobs, warpMatrix, (1080, 1080))
        else:
            imageBlobsWarped = imageBlobs

        # Calibrate the warped image of fish.
        #print("Calibrating {} image {}.".format(imagePath.rsplit("/", 1)[-2], name))
        imageRGBUndistorted = cv2.undistort(imageRGB, matrix, distortion, None, newCameraMatrix)
        imageBlobsUndistorted = cv2.undistort(imageBlobsWarped, matrix, distortion, None, newCameraMatrix)


        # Crop image to region of interest
        x, y, width, height = regionsOfInterest
        imageRGBUndistorted = imageRGBUndistorted[y:y + height, x:x + width]
        imageBlobsUndistorted = imageBlobsUndistorted[y:y + height, x:x + width]
        ret, imageBlobsUndistorted = cv2.threshold(imageBlobsUndistorted, 200, 255, 0)

        #self.showImage([imageBlobs, imageBlobsUndistorted])
        # newFileName = outputPathCalibration.format("calibrated" + fileName.rsplit('\\', 1)[-1])
        # print("Writing to: ", newFileName)
        # cv2.imwrite(newFileName, imageUndistorted)


        return [imageRGBUndistorted, imageBlobsUndistorted]


if __name__ == "__main__":
    groups = [4]#, 9, 15, 19]
    calibrator = ImageCalibrator()
    sizeFinder = SizeFinder()
    for group in groups:
        print("Running calibration for group {}".format(group))
        imageBlobs = cv2.imread(r"C:\P3OutData\Merged\group_4\FinalTH\00002Final.png", cv2.IMREAD_UNCHANGED)
        imageRGB = cv2.imread(r"C:\FishProject\group_4\rs\rgb\00002.png", cv2.IMREAD_UNCHANGED)

        calibrationImages = glob.glob(r"C:\FishProject\group_4\calibration\rs\*.png")
        calibration = calibrator.getImageCalibration(calibrationImages)
        #calibrated = calibrator.calibrateImage(imageRGB, imageBlobs, calibration)
        calibrationImagesOutput = glob.glob(r"C:\P3OutData\Example\Checkerboard\*Uncalibrated.png")
        for image in calibrationImagesOutput:
            name = image.rsplit('\\', 1)[-1]
            name = name.rsplit('.', 1)[0]
            name = name.rsplit('Uncalibrated', 1)[0]
            print("Calibrating {}".format(name))
            image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
            images = calibrator.calibrateImage(image, image, calibration)
            cv2.imwrite(r"C:\P3OutData\Example\Checkerboard\{}xCalibrated.png".format(name), images[0])

