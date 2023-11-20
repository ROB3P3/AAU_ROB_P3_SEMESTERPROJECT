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
    imMask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(imCopy, imMask, (0,0), 255)

    imCopy = cv2.bitwise_not(imCopy)

    imReturn = image | imCopy
    return imReturn

def thresholdDepthMap(path):
    """Thresholds the depth map to isolate the fish"""
    rawDepthImage = o3d.io.read_image(path)
    jsonFilePath = path.replace(".png", ".json")
    
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
    
    rgbFilePath = path.replace("depth", "rgb")
    rawRGBImage = o3d.io.read_image(rgbFilePath)
    rgbdImage = o3d.geometry.RGBDImage.create_from_color_and_depth(rawRGBImage, rawDepthImage, convert_rgb_to_intensity=False)
    
    depthPointCloud = o3d.geometry.PointCloud.create_from_depth_image(rawDepthImage, cameraIntrinsics)
    rgbDepthPointCloud = o3d.geometry.PointCloud.create_from_rgbd_image(rgbdImage, cameraIntrinsics)
    
    rgbDepthPointCloud.scale(10, (0, 0, 0))
    # skal have implementeret dynamisk rotation af y-aksen
    rgbDepthPointCloud.rotate(rgbDepthPointCloud.get_rotation_matrix_from_xyz((np.pi*(3/180), np.pi*(1/180), 0)))
    
    coordinateFrame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=2, origin=(0, 0, 0))
    
    
    # find minimum x-value
    min = rgbDepthPointCloud.get_min_bound()
    xMin = min[0]
    max = rgbDepthPointCloud.get_max_bound()
    xMax = max[0]
    
    for row in np.asarray(rgbDepthPointCloud.points):
        if row[0] < -1.5 and row[0] > -3 and row[2] < 10:
            if row[0] > xMin:
                xMin = row[0]
    
    colorArray = np.asarray(rgbDepthPointCloud.colors)
    xMid = -1
    zMin = 10.4
    zMax = 11.07
    zDiff = abs(zMin - zMax)
    
    for i, row in enumerate(np.asarray(rgbDepthPointCloud.points)):
        if row[0] > xMin:
            if row[0] < xMid:
                # scaling the z threshold based on the difference between the min and mid x values
                zThreshold = 10.95 + (((11.04 - 10.95) / abs(xMid - xMin)) * abs(row[0] - xMin))
            else:
                zThreshold = 11.04
            
            if row[2] < zThreshold:
                z_color = 0.2 + (((1 - 0.2) / zDiff) * (row[2] - zMin))
                colorArray[i] = [z_color, 0, 0]
    
    rgbDepthPointCloud.colors = o3d.utility.Vector3dVector(colorArray)
    
    image = pointCloudToImage(rgbDepthPointCloud, cameraIntrinsics)
    thresholdedImage = thresholdImageBlue(image)
    filledImage = fillHoles(thresholdedImage)
    
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name=path)
    vis.add_geometry(rgbDepthPointCloud)
    vis.add_geometry(coordinateFrame)
    vis.get_view_control().convert_from_pinhole_camera_parameters(o3d.io.read_pinhole_camera_parameters("C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/ScreenCamera_2023-11-17-12-48-01.json"))
    vis.run()
    vis.destroy_window()
    
    return filledImage

# function to find angle between two 3d vectors
def angleBetweenVectors(v1, v2):
    """Finds the angle between two 3D vectors"""
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    angle = np.arccos(dot / norm)
    return angle
    
def pointCloudToImage(pointCloud, intrinsics):
    """Converts a point cloud to an image using the given camera intrinsics"""
    points = np.asarray(pointCloud.points)
    colors = np.asarray(pointCloud.colors)
    
    points = np.transpose(points)
    
    points = np.matmul(intrinsics.intrinsic_matrix, points)
    points = np.transpose(points)
    points = points[:, :2] / points[:, 2:]
    points = points.astype(int)
    
    image = np.zeros((intrinsics.height, intrinsics.width, 3))
    for i in range(points.shape[0]):
        image[points[i, 1], points[i, 0]] = colors[i]
        
    image = (image * 255).astype('uint8')
    return image

def thresholdImageBlue(image):
    """Thresholds the image to only show the blue pixels"""
    lowerBlue = np.array([20, 0, 0])
    upperBlue = np.array([255, 0, 0])
    
    mask = cv2.inRange(image, lowerBlue, upperBlue)
    result = cv2.bitwise_and(image, image, mask=mask)
    
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    
    result[result > 0] = 255
    
    return result

def thresholdImage(path):
    """Thresholds image based on color and shape"""
    # convert to grayscale
    # median filter with radius 10
    # unsharp mask with radius 15 and weight 0.9
    # threshold from 0 to 125
    # median filter with radius 15
    # fill holes
    path = path.replace("depth", "rgb")
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    medianBlurImage = cv2.medianBlur(image, (10*2)+1)
    unsharpenedImage = Image.fromarray(medianBlurImage)
    unsharpenedImage = unsharpenedImage.filter(ImageFilter.UnsharpMask(radius=15, percent=900))
    unsharpenedImage = np.array(unsharpenedImage)
    ret, thresholdedImage = cv2.threshold(unsharpenedImage, 125, 255, cv2.THRESH_BINARY_INV)
    medianBlurImage2 = cv2.medianBlur(thresholdedImage, (15*2)+1)
    
    # remove this when the cropped images are used as input
    for y, row in enumerate(medianBlurImage2):
        for x, col in enumerate(row):
            if x < 700 and col == 255:
                medianBlurImage2[y][x] = 0
                
    filledImage = fillHoles(medianBlurImage2)
    
    """ cv2.imshow("image", image)
    cv2.imshow("median blur", medianBlurImage)
    cv2.imshow("unsharp mask", unsharpenedImage)
    cv2.imshow("thresholding", thresholdedImage)
    cv2.imshow("median blur 2", medianBlurImage2)
    cv2.imshow("filled image", filledImage)
    cv2.waitKey(0) """
    return filledImage

if __name__ == "__main__":
    groups = [9, 15, 19]
    imageNum = 66
    
    for group in groups:
        rootPath = "C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/autofish_sample/group_{}".format(group)
        outputPath = "C:/Users/takek/Dropbox/PC (3)/Documents/University/Semester 3/P3/Project/Data/output/group_{}".format(group)
        
        for i in range(2, imageNum + 1):
            if i < 10:
                imagePath = rootPath + "/rs/depth/0000" + str(i) + ".png"
            else:
                imagePath = rootPath + "/rs/depth/000" + str(i) + ".png"
            img1 = thresholdDepthMap(imagePath)
            img2 = thresholdImage(imagePath)
            img3 = img1 + img2
            img3 = fillHoles(img3)
            #cv2.imshow("image", img1)
            #cv2.imshow("image2", img2)
            cv2.imshow("group_{}/{}".format(group, i), img3)
            cv2.waitKey(0)
            
        