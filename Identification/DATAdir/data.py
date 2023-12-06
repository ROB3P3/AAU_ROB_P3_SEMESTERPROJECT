import cv2
import open3d as o3d
import json

class ImageData:
    """Class for handelign the data needed for each image"""
    def __init__(self, imagePath, index, group):
        """initialized with a path and an index"""
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
        """Sets and execute the auto cropping on the Image"""
        self.cropper = cropper
        self.cropper.setImage(self.imgGray)
        self.cropper.crop()
        self.cropedImage = cropper.imgCropped

    def setColourThresholdedImage(self, image):
        """ Set the binary image wich represent the color threshold applied to the original PNG"""
        self.colourThrsholdedImage = image
    
    def setDepthThresholding(self, image):
        """ Set the image wich represents the original"""
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

    def setCalibratedImages(self, imageRGB, imageThresholded):
        self.calibratedRGBImage = imageRGB
        self.calibratedThresholdedImage = imageThresholded

    def setAtributesFromSizeFinder(self, sizeReturnList):
        self.fishLenghts = sizeReturnList[0]
        self.fishOrientations = sizeReturnList[1]
        self.annotatedImage = sizeReturnList[2]
        self.boundingBoxImage = sizeReturnList[3]
        self.averagePoints = sizeReturnList[4]
        self.separateContours = sizeReturnList[5]
        self.extremePointList1 = sizeReturnList[6]
        self.extremePointList2 = sizeReturnList[7]
        self.fishAreas = sizeReturnList[8]
    
    def setAttributesFromGrippingPoints(self, gPointsOutput):
        self.fishGrippingPoints = gPointsOutput[0]
        self.fishWidths = gPointsOutput[1]
    
    def setAverageHSV(self, avgHSVList):
        self.fishAverageHSV = avgHSVList
    
    def setSpeciesFromClassifier(self, speciesList):
        self.fishSpecies = speciesList