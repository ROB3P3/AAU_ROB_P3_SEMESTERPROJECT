import cv2
import numpy as np
import open3d as o3d
import json
import os
from PIL import Image, ImageFilter
from LOGIKdir.AutoCrop import Cropper


# ******************************************* Functions for thresholding ****************************************
class Thresholder:
    # The class wich crops the images on the provided file path (skal måske laves om til at køre på img fra tidligere kode i stedet)

    def __init__(self):
        print("TH initialized")

    def fillHoles(self, image):
        """Fills holes in binary image"""
        imCopy = image.copy()
        h, w = imCopy.shape[:2]
        # Creates a mask based on input image
        imMask = np.zeros((h + 2, w + 2), np.uint8)
        # Fills the holes in the image
        cv2.floodFill(imCopy, imMask, (0, 0), 255)
        # Inverts it to make the holes white, and background black
        imCopy = cv2.bitwise_not(imCopy)
        # Combines the original image with the inverted image
        imReturn = image | imCopy
        return imReturn

    def pointCloudToImage(self, pointCloud, intrinsics):
        """Converts a point cloud to an image using the given camera intrinsics"""
        points = np.asarray(pointCloud.points)
        colors = np.asarray(pointCloud.colors)

        # Transposes the points array to change shape from Nx3 to 3xN, to make the matrix multiplication with the intrinsics matrix possible
        points = np.transpose(points)
        points = np.matmul(intrinsics.intrinsic_matrix, points)
        # Transposes the points array back to its original shape
        points = np.transpose(points)
        # Divides the x and y values by the z value to convert points form homogeneous coordinates to cartesian coordinates
        cartesianPoints = points[:, :2] / points[:, 2:]
        cartesianPoints = cartesianPoints.astype(int)

        # Creates an empty image with the same dimensions as the original image
        image = np.zeros((intrinsics.height, intrinsics.width, 3))
        imageZ = np.zeros((intrinsics.height, intrinsics.width, 1))
        # Add an imageZ that is the same dimensions but contains the z-values of the points
        # return this image, and calculate the z-point of the gripping points under GrippingPoints.py

        # Sets the color of each pixel to the color of the corresponding point
        for i in range(cartesianPoints.shape[0]):
            if 0 <= cartesianPoints[i, 1] < intrinsics.height and 0 <= cartesianPoints[i, 0] < intrinsics.width:
                image[cartesianPoints[i, 1], cartesianPoints[i, 0]] = colors[i]
                imageZ[cartesianPoints[i, 1], cartesianPoints[i, 0]] = points[i, 2]

        # Converts the image to the range [0, 255]
        image = (image * 255).astype('uint8')

        return image, imageZ

    def thresholdImageBlue(self, image):
        """Thresholds the image to only show the blue pixels"""
        # Define the lower and upper threshold of the blue color
        lowerBlue = np.array([20, 0, 0])
        upperBlue = np.array([255, 0, 0])

        # Thresholds the image
        mask = cv2.inRange(image, lowerBlue, upperBlue)
        result = cv2.bitwise_and(image, image, mask=mask)

        # Turns the image binary
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        result[result > 0] = 255

        return result

    def thresholdImage(self, imageData):
        """Thresholds image based on color and shape"""
        print("Thresholding colour:")
        # Applies a median filter with radius 10
        medianBlurImage = cv2.medianBlur(imageData.imgGray, (10 * 2) + 1)
        # Applies an unsharp mask with radius 15 and weight 0.9
        unsharpenedImage = Image.fromarray(medianBlurImage)
        unsharpenedImage = unsharpenedImage.filter(ImageFilter.UnsharpMask(radius=15, percent=900))
        unsharpenedImage = np.array(unsharpenedImage)
        # Thresholds the image from 0 to 125
        ret, thresholdedImage = cv2.threshold(unsharpenedImage, 125, 255, cv2.THRESH_BINARY_INV)
        # Applies another median filter with radius 15
        medianBlurImage2 = cv2.medianBlur(thresholdedImage, (15 * 2) + 1)

        # remove this when the cropped images are used as input
        for y, row in enumerate(medianBlurImage2):
            for x, col in enumerate(row):
                if (x < imageData.cropper.xStart and col == 255) or (x > imageData.cropper.xEnd and col == 255):
                    medianBlurImage2[y][x] = 0

        # Fills holes 
        filledImage = self.fillHoles(medianBlurImage2)
        imageData.setColourThresholdedImage(filledImage)

        return filledImage

    def thresholdDepthMap(self, imageData):
        """Thresholds the depth map to isolate the fish"""
        print("Thresholding depth:")
        rawDepthImage = imageData.rawDepthImage

        intrinsics = imageData.intrinsics

        cameraIntrinsics = o3d.camera.PinholeCameraIntrinsic()
        cameraIntrinsics.set_intrinsics(
            intrinsics['width'],
            intrinsics['height'],
            intrinsics['fx'],
            intrinsics['fy'],
            intrinsics['cx'],
            intrinsics['cy'],
        )

        # Create depth pointclouds from depth-data
        rawRGBImage = o3d.io.read_image(imageData.imagePath)
        rgbdImage = o3d.geometry.RGBDImage.create_from_color_and_depth(rawRGBImage, rawDepthImage,
                                                                       convert_rgb_to_intensity=False)

        depthPointCloud = o3d.geometry.PointCloud.create_from_depth_image(rawDepthImage, cameraIntrinsics)
        rgbDepthPointCloud = o3d.geometry.PointCloud.create_from_rgbd_image(rgbdImage, cameraIntrinsics)

        # The pointcloud is scaled 10x to make it easier to work with
        rgbDepthPointCloud.scale(10, (0, 0, 0))

        # Coordinate frame to show the orientation of the pointcloud, and camera position
        coordinateFrame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2, origin=(0, 0, 0))

        pointArray = np.asarray(rgbDepthPointCloud.points)
        colorArray = np.asarray(rgbDepthPointCloud.colors)
        min = rgbDepthPointCloud.get_min_bound()
        xMin = min[0]
        max = rgbDepthPointCloud.get_max_bound()
        xMax = max[0]
        xMid = -1
        zMin = 10.4
        zMax = 11.07
        zDiff = abs(zMin - zMax)

        avgZ = 0
        avgZPoints = 0

        for row in pointArray:
            # Finds the minimum x-value in the ROI
            if row[0] < -1.5 and row[0] > -3 and row[2] < 10:
                if row[0] > xMin:
                    xMin = row[0]
            # Finds the average z-value in the ROI
            if row[0] > xMin:
                if row[2] < 12 and row[2] > 10:
                    avgZ += row[2]
                    avgZPoints += 1
        avgZ = avgZ / avgZPoints

        # Y-rotation is scaled on the average z-value in the ROI
        rotY = 1 + (((2.2 - 1) / (11.15 - 11.07)) * (avgZ - 11.07))
        rgbDepthPointCloud.rotate(
            rgbDepthPointCloud.get_rotation_matrix_from_xyz((np.pi * (3 / 180), np.pi * (rotY / 180), 0)))

        # Thresholds the pointcloud to segment the fish
        for i, row in enumerate(pointArray):
            if row[0] > xMin:
                # The depth data is closer right at the camera, and so the threshold around this area is scaled based on the x-value
                # Outside of this area a global threshold is used
                if row[0] < xMid:
                    # scaling the z threshold based on the difference between the min and mid x values
                    zThreshold = 10.95 + (((11.04 - 10.95) / abs(xMid - xMin)) * abs(row[0] - xMin))
                else:
                    zThreshold = 11.04

                if row[2] < zThreshold:
                    # Scales the color of the point based on the z-value
                    z_color = 0.2 + (((1 - 0.2) / zDiff) * (row[2] - zMin))
                    colorArray[i] = [z_color, 0, 0]

        # Changes the color of the pointcloud to show the thresholded points
        rgbDepthPointCloud.colors = o3d.utility.Vector3dVector(colorArray)

        # Converts the pointcloud to a 2D RGB image, thresholds it to make it binary, and fills the holes
        image, imageZ = self.pointCloudToImage(rgbDepthPointCloud, cameraIntrinsics)
        thresholdedImage = self.thresholdImageBlue(image)
        medianImage = cv2.medianBlur(thresholdedImage, (10 * 2) + 1)
        filledImage = self.fillHoles(medianImage)

        # Visualizer to show thresholded pointcloud
        # Uncomment to view visualizer
        """ vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=str(imageData.index))
        vis.add_geometry(rgbDepthPointCloud)
        vis.add_geometry(coordinateFrame)
        vis.get_view_control().convert_from_pinhole_camera_parameters(o3d.io.read_pinhole_camera_parameters("C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/ScreenCamera_2023-11-17-12-48-01.json"))
        vis.run()
        vis.destroy_window() """

        return filledImage, imageZ

    # ******************************************* END Functions for thresholding ****************************************

    # ******************************************* Functions for BLOB seberation ****************************************
    def findEdge(self, image):
        """Find edges in a an image, input is a colour BGR image"""
        imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        imageGraBlur = cv2.medianBlur(imageGray, 7)

        # udgangspunkt var 90, 190
        imageEdgeBlur = cv2.Canny(imageGraBlur, 60, 190)
        element = cv2.getStructuringElement(1, (2 * 2 + 1, 2 * 2 + 1),
                                            (2, 2))

        imageEdgeBlurDilated = cv2.dilate(imageEdgeBlur, element)

        return imageEdgeBlurDilated

    def seperate(self, imageThreshold, imageEdges):
        """Separates the fish from the each other, input is a binary image and an edge image"""
        image = cv2.subtract(imageThreshold, imageEdges)

        element = cv2.getStructuringElement(1, (2 * 1 + 1, 2 * 1 + 1),
                                            (1, 1))
        imageErode = cv2.erode(image, element)

        contour = cv2.findContours(imageErode, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]

        for cnt in contour:
            cv2.drawContours(imageErode, [cnt], 0, 255, -2)
        return imageErode

    # ***************************************** Main funktion describing the execution of the class *************************************
    def isolate(self, outputDataRootPath, imageData):
        """returns a binary image of the isolated fish, with some separation, and Saves all
        relevant images to the outputDataRootPath
        This function also updates data in the imageData object """

        imageData.setCropper(Cropper())

        imageData.setColourThresholdedImage(self.thresholdImage(imageData))

        imageData.setDepthThresholding(self.thresholdDepthMap(imageData))

        # combine depth and colour thresholdings to a raw combination
        imageData.setRawThresholdedImage(imageData.depthThresholding + imageData.colourThrsholdedImage)

        # fill holes in the raw thresholded image
        imageData.setFilledThresholdedImage(self.fillHoles(imageData.rawThresholdedImage))

        # find edges in the raw thresholded image
        imageData.setImageEdges(self.findEdge(imageData.img))

        imageData.setSeperatedThresholdedImage(self.seperate(imageData.filledThresholdedImage, imageData.imageEdges))

        os.chdir("{}/group_{}/THData".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "CP.png", imageData.cropedImage)
        cv2.imwrite(str(imageData.index).zfill(5) + "TH.png", imageData.filledThresholdedImage)
        cv2.imwrite(str(imageData.index).zfill(5) + "Final.png", imageData.seperatedThresholdedImage)
        cv2.imwrite(str(imageData.index).zfill(5) + "Edge.png", imageData.imageEdges)
        cv2.imwrite(str(imageData.index).zfill(5) + "ColourTH.png", imageData.colourThrsholdedImage)
        cv2.imwrite(str(imageData.index).zfill(5) + "DepthTH.png", imageData.depthThresholding)

        os.chdir("{}/group_{}/CP".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "CP.png", imageData.cropedImage)
        os.chdir("{}/group_{}/THSum".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "THSum.png", imageData.filledThresholdedImage)
        os.chdir("{}/group_{}/FinalTH".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "Final.png", imageData.seperatedThresholdedImage)
        os.chdir("{}/group_{}/Edge".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "Edge.png", imageData.imageEdges)
        os.chdir("{}/group_{}/ColourTH".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "ColourTH.png", imageData.colourThrsholdedImage)
        os.chdir("{}/group_{}/DepthTH".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "DepthTH.png", imageData.depthThresholding)
        os.chdir("{}/group_{}/FinalTH".format(outputDataRootPath, imageData.group))
        cv2.imwrite(str(imageData.index).zfill(5) + "Final.png", imageData.seperatedThresholdedImage)

        return (imageData.seperatedThresholdedImage)
