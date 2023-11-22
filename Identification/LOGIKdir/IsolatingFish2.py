import cv2
import numpy as np
import open3d as o3d
import json
import os
from PIL import Image, ImageFilter

def fillHoles(image):
    """Fills holes in binary image"""
    imCopy = image.copy()
    h, w = imCopy.shape[:2]
    # Creates a mask based on input image
    imMask = np.zeros((h + 2, w + 2), np.uint8)
    # Fills the holes in the image
    cv2.floodFill(imCopy, imMask, (0,0), 255)
    # Inverts it to make the holes white, and background black
    imCopy = cv2.bitwise_not(imCopy)
    # Combines the original image with the inverted image
    imReturn = image | imCopy
    return imReturn

def pointCloudToImage(pointCloud, intrinsics):
    """Converts a point cloud to an image using the given camera intrinsics"""
    points = np.asarray(pointCloud.points)
    colors = np.asarray(pointCloud.colors)
    
    # Transposes the points array to change shape from Nx3 to 3xN, to make the matrix multiplication with the intrinsics matrix possible
    points = np.transpose(points)
    points = np.matmul(intrinsics.intrinsic_matrix, points)
    # Transposes the points array back to its original shape
    points = np.transpose(points)
    # Divides the x and y values by the z value to convert points form homogeneous coordinates to cartesian coordinates
    points = points[:, :2] / points[:, 2:]
    points = points.astype(int)
    
    # Creates an empty image with the same dimensions as the original image
    image = np.zeros((intrinsics.height, intrinsics.width, 3))
    
    # Sets the color of each pixel to the color of the corresponding point
    for i in range(points.shape[0]):
        if 0 <= points[i, 1] < intrinsics.height and 0 <= points[i, 0] < intrinsics.width:
            image[points[i, 1], points[i, 0]] = colors[i]
    
    # Converts the image to the range [0, 255]
    image = (image * 255).astype('uint8')
    return image

def thresholdImageBlue(image):
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

def thresholdImage(path):
    """Thresholds image based on color and shape"""
    # Finds path to RGB image of corresponding depth data
    path = path.replace("depth", "rgb")
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    # Applies a median filter with radius 10
    medianBlurImage = cv2.medianBlur(image, (10*2)+1)
    # Applies an unsharp mask with radius 15 and weight 0.9
    unsharpenedImage = Image.fromarray(medianBlurImage)
    unsharpenedImage = unsharpenedImage.filter(ImageFilter.UnsharpMask(radius=15, percent=900))
    unsharpenedImage = np.array(unsharpenedImage)
    # Thresholds the image from 0 to 125
    ret, thresholdedImage = cv2.threshold(unsharpenedImage, 125, 255, cv2.THRESH_BINARY_INV)
    # Applies another median filter with radius 15
    medianBlurImage2 = cv2.medianBlur(thresholdedImage, (15*2)+1)
    
    # remove this when the cropped images are used as input
    for y, row in enumerate(medianBlurImage2):
        for x, col in enumerate(row):
            if x < 700 and col == 255:
                medianBlurImage2[y][x] = 0
    
    # Fills holes 
    filledImage = fillHoles(medianBlurImage2)
    return filledImage

def thresholdDepthMap(path):
    """Thresholds the depth map to isolate the fish"""
    rawDepthImage = o3d.io.read_image(path)
    jsonFilePath = path.replace(".png", ".json")
    
    # Define camera intrinsics from depth-map json files
    with open(jsonFilePath, 'r') as file:
        intrinsics = json.load(file)
        
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
    rgbFilePath = path.replace("depth", "rgb")
    rawRGBImage = o3d.io.read_image(rgbFilePath)
    rgbdImage = o3d.geometry.RGBDImage.create_from_color_and_depth(rawRGBImage, rawDepthImage, convert_rgb_to_intensity=False)
    
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
    rotY = 1 + (((2.2 - 1) / abs(11.15 - 11.07)) * (avgZ - 11.07))
    rgbDepthPointCloud.rotate(rgbDepthPointCloud.get_rotation_matrix_from_xyz((np.pi*(3/180), np.pi*(rotY/180), 0)))
    
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
    image = pointCloudToImage(rgbDepthPointCloud, cameraIntrinsics)
    thresholdedImage = thresholdImageBlue(image)
    medianImage = cv2.medianBlur(thresholdedImage, (10*2)+1)
    filledImage = fillHoles(medianImage)
    
    # Visualizer to show thresholded pointcloud
    # Uncomment to view visualizer
    """ vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=path)
    vis.add_geometry(rgbDepthPointCloud)
    vis.add_geometry(coordinateFrame)
    vis.get_view_control().convert_from_pinhole_camera_parameters(o3d.io.read_pinhole_camera_parameters("C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/ScreenCamera_2023-11-17-12-48-01.json"))
    vis.run()
    vis.destroy_window() """
    
    return filledImage

if __name__ == "__main__":
    groups = [4, 9, 15, 19]
    imageNum = 66
    
    for group in groups:
        rootPath = "C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/autofish_sample/group_{}".format(group)
        outputPath = "C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/Data/output/group_{}".format(group)
        
        for i in range(2, imageNum + 1):
            print("group_{}: {}".format(group, i))
            if i < 10:
                imagePath = rootPath + "/rs/depth/0000" + str(i) + ".png"
            else:
                imagePath = rootPath + "/rs/depth/000" + str(i) + ".png"
            thresholdedImage = thresholdDepthMap(imagePath) + thresholdImage(imagePath)
            thresholdedImage = fillHoles(thresholdedImage)
            os.chdir("C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/Data/output/group_{}".format(group))
            cv2.imwrite("0000" + str(i) + ".png", thresholdedImage)
            """ cv2.imshow("group_{}/{}".format(group, i), thresholdedImage)
            cv2.waitKey(0) """
            
        