import numpy as np
import cv2 as cv
import glob
import math


def removeSides(image):
    """Function to remove the sides of the PNG images"""
    # manually found the x-coordinates for the sides on the top and bottom
    xLeftTop = 666
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


def showImage(image):
    """Function to show an image until 0 is pressed"""
    cv.imshow("Image", image)
    while True:
        k = cv.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)


def calibrateImage(imageType):
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)
    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d point in real world space
    imgpoints = []  # 2d points in image plane.
    imgError = []
    imageCorrection = []
    images = glob.glob(r'DATAdir/RGB/Calibration/{}/*.png'.format(imageType))
    for fname in images:
        print(fname)
        image = cv.imread(fname)
        if imageType == "png": image = removeSides(image)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (9, 6), cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)
        # If found, add object points, image points (after refining them)
        if ret == True:
            print("Ret = True")
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            # Draw and display the corners
            cv.drawChessboardCorners(image, (9, 6), corners2, ret)

            # Begin undistorting
            ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

            h, w = image.shape[:2]
            newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

            # undistort
            dst = cv.undistort(image, mtx, dist, None, newcameramtx)
            imageCorrection.append(dst)

            mean_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
                error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
                mean_error += error
                totalError = mean_error / len(objpoints)
            print("total error: {}".format(totalError))
            imgError.append(totalError)

    leastError = imgError.index(min(imgError))
    worstError = imgError.index(max(imgError))
    medianError = sorted(imgError)[round(len(imgError)/2)]

    print("Least error: ", images[leastError])
    print("Worst error: ", images[worstError])
    print("Median error: ", images[imgError.index(medianError)])

    cv.imshow("Minimum Error", imageCorrection[leastError])
    cv.imshow("Maximum Error", imageCorrection[worstError])
    cv.imshow("Median Error", imageCorrection[imgError.index(medianError)])
    while True:
        k = cv.waitKey(0) & 0xFF
        if k == 48:
            break
        print(k)

    cv.destroyAllWindows()


if __name__ == "__main__":
    calibrateImage("png")
