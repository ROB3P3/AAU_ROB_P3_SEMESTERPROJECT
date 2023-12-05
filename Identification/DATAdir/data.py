import cv2
import open3d as o3d
import json

class ImageData:
    "Class for handelign the data needed for each image"
    def __init__(self, imagePath, index, group):
        "initialized with a path and an index"
        self.index = index
        self.group = group
        self.imagePath = imagePath
        self.depthPath = imagePath.replace("rgb", "depth")

        self.img = cv2.imread(imagePath)
        self.imgGray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        self.rawDepthImage = o3d.io.read_image(self.depthPath)
        self.jsonFilePath = self.depthPath.replace(".png", ".json")
        # Define camera intrinsics from depth-map json files
        with open(self.jsonFilePath, 'r') as file:
            self.intrinsics = json.load(file)

    def setCropper(self, cropper):
        "Sets and execute the auto cropping on the Image"
        self.cropper = cropper
        self.cropper.setImage(self.imgGray)
        self.cropper.crop()
        self.cropedImage = cropper.imgCropped

    def setColourThresholdedImage(self, image):
        " Set the binary image wich represent the color threshold applied to the original PNG"
        self.colourThrsholdedImage = image
    
    def setDepthThresholding(self, image):
        " Set the image wich represents the binary threshold of the original depth image"
        self.depthThresholding = image

    def setRawThresholdedImage(self, image):
        " Set the combined color and depth thresholded images"
        self.rawThresholdedImage = image
    
    def setThresholdedImage(self, image):
        " "
        self.filledThresholdedImage = image

    def setFilledThresholdedImage(self, image):
        " Set the filled combined thresholded image"
        self.filledThresholdedImage = image

    def setImageEdges(self, image):
        " Set the image containing the edges found on the original PNG. The edges are set to WHITE"
        self.imageEdges = image
    
    def setSeperatedThresholdedImage(self, image):
        " Set the image where the fish are seperated by the edges found in the original PNG"
        self.seperatedThresholdedImage = image

    def setCalibratedRGBImage(self, image):
        self.calibratedRGBImage = image

    def setCalibratedThresholdedImage(self, image):
        self.calibratedThresholdedImage = image

    def setAtributesFromSizeFinder(self, sizeRreturnList):
        " Handle the output of the SizeFinder function"
        self.fishLenghts = sizeRreturnList[0]
        self.fishOrientations = sizeRreturnList[1]
        self.annotatedImage = sizeRreturnList[2]
        self.boundingBoxImage = sizeRreturnList[3]
        self.averagePoints = sizeRreturnList[4]
        self.separateContours = sizeRreturnList[5]