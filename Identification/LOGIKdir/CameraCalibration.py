import numpy as np
import cv2
import glob
import os


def clearDirectory(path):
    """Delete all files in the given folder"""
    print("Deleting files in: ", path)
    files = glob.glob(path)
    for file in files:
        #print("Deleted ", file)
        os.remove(file)


def showImage(images):
    """Function to show an array of images until 0 is pressed"""
    for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
    while True:
        k = cv2.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)


def WarpPerspective(image, fileName):
    """Warp the perspective of a 1920x1080 PNG in group 9 image to help account for the angle of the camera.
    Takes a PNG image and warps it to a 1080x1080 pixel image containing only the conveyor."""

    # Points in the orignal image indicating where to warp perspective to.
    orignalPoints = np.float32([[666, 0], [677, 1080], [1824, 0], [1864, 1080]])
    # What the originalPoints new values should be in the perspective warped image
    newPoints = np.float32([[0, 0], [0, 1080], [1080, 0], [1080, 1080]])
    # Warp all checkerboard images and put them in their own folder.
    #print("Warping perspective of {}.".format(fileName))
    warpMatrix = cv2.getPerspectiveTransform(orignalPoints, newPoints)
    # Use the values from above to warp the image to a 1080x1080 pixel image.
    return cv2.warpPerspective(image, warpMatrix, (1080, 1080))


def getImageCalibration(path):
    """Gets the values required for undistorting and image based on a checkerboard."""
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

    # Extracting path of individual images stored in a given directory.
    images = glob.glob(path + "/calibration/*.png")
    print(images)


    for fileName in images:
        name = fileName.rsplit('\\', 1)[-1]
        image = cv2.imread(fileName, cv2.IMREAD_UNCHANGED)

        # Warp perspective of board
        image = WarpPerspective(image, name)

        print("Finding Checkerboards for {}.".format(name))
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
            imageDrawn = cv2.drawChessboardCorners(image, CHECKERBOARD, corners2, retval)
            #showImage([imageDrawn])
        else:
            print("Can't find enough corners in {}.".format(name))
            # showImage([image])

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


def calibrateImage(correctionValues, mainPath, outputPath):
    """Apllies the calibration values found in getImageCalibration() to the images in the group"""
    # Clear output folder to ensure only the newest files.
    fishPath = mainPath + "rs/rgb/*.png"
    outputPath = outputPath + "{}"
    clearDirectory(outputPath.format("*"))

    # Get all images to calibrate
    images = glob.glob(fishPath)
    retval, matrix, distortion, rotationVector, translationVector, newCameraMatrix, regionsOfInterest = correctionValues
    i = 1
    for fileName in images:
        name = fileName.rsplit('\\', 1)[-1]
        image = cv2.imread(fileName)

        # Warp perspective on the fish images.
        image = WarpPerspective(image, name)

        # Calibrate the warped image of fish.
        print("Calibrating {} image {}.".format(fishPath.rsplit("/", 1)[-2], name))
        imageUndistorted = cv2.undistort(image, matrix, distortion, None, newCameraMatrix)

        # Crop image to region of interest
        x, y, width, height = regionsOfInterest
        imageUndistorted = imageUndistorted[y:y + height, x:x + width]

        # showImage([imageUndistorted])
        newFileName = outputPath.format("calibrated" + fileName.rsplit('\\', 1)[-1])
        i += 1

        cv2.imwrite(newFileName, imageUndistorted)
    #print("Finished warping and calibrating all fish images in group {}.".format(group))


if __name__ == "__main__":
    groups = [4, 9, 15, 19]

    for group in groups:
        print("Running calibration for group {}".format(group))
        mainPath = "C:/FishProject/group_{}/"
        outputPath = "C:/FishProject/group_{}/output/WarpedCalibratedFish/"
        calibration = getImageCalibration(mainPath.format(group))
        calibrateImage(calibration, mainPath.format(group), outputPath.format(group))
