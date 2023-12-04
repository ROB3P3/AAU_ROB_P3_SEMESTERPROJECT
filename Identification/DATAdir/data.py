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
        self.colourThrsholdedImage = image
    
    def setDepthThresholding(self, image):
        self.depthThresholding = image

    def setRawThresholdedImage(self, image):
        self.rawThresholdedImage = image
    
    def setThresholdedImage(self, image):
        self.filledThresholdedImage = image

    def setFilledThresholdedImage(self, image):
        self.filledThresholdedImage = image

    def setImageEdges(self, image):
        self.imageEdges = image
    
    def setSeperatedThresholdedImage(self, image):
        self.seperatedThresholdedImage = image

    def setAtributesFromSizeFinder(self, sizeRreturnList):
        self.fishLenghts = sizeRreturnList[0]
        self.fishOrientations = sizeRreturnList[1]
        self.annotatedImage = sizeRreturnList[2]
        self.boundingBoxImage = sizeRreturnList[3]
        self.averagePoints = sizeRreturnList[4]
        self.separateContours = sizeRreturnList[5]