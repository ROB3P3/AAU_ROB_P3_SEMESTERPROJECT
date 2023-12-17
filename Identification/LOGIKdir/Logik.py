import cv2
import numpy as np
import math
import os
import multiprocessing as mp
import csv
from fractions import Fraction
from LOGIKdir.Sizefinder import SizeFinder
from LOGIKdir.IsolatingFish2 import Thresholder
from LOGIKdir.GrippingPoints import GrippingPoints
from LOGIKdir.Classifier import Classifier
from DATAdir.data import ImageData
from LOGIKdir.CameraCalibration import ImageCalibrator
import time
import glob


def pathingSetup(group, rootPath):
    """Formats the file setup the program need. Run this before any of the image processing"""
    if not os.path.exists("{}/group_{}/Size".format(rootPath, group)):
        os.makedirs("{}/group_{}/Size".format(rootPath, group))
    if not os.path.exists("{}/group_{}/THData".format(rootPath, group)):
        os.makedirs("{}/group_{}/THData".format(rootPath, group))
    if not os.path.exists("{}/group_{}/FinalTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/FinalTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/DepthTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/DepthTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/CP".format(rootPath, group)):
        os.makedirs("{}/group_{}/CP".format(rootPath, group))
    if not os.path.exists("{}/group_{}/Edge".format(rootPath, group)):
        os.makedirs("{}/group_{}/Edge".format(rootPath, group))
    if not os.path.exists("{}/group_{}/ColourTH".format(rootPath, group)):
        os.makedirs("{}/group_{}/ColourTH".format(rootPath, group))
    if not os.path.exists("{}/group_{}/THSum".format(rootPath, group)):
        os.makedirs("{}/group_{}/THSum".format(rootPath, group))
    if not os.path.exists("{}/group_{}/GripPoints".format(rootPath, group)):
        os.makedirs("{}/group_{}/GripPoints".format(rootPath, group))
    if not os.path.exists("{}/group_{}/Results".format(rootPath, group)):
        os.makedirs("{}/group_{}/Results".format(rootPath, group))


def taskHandeler(indexFileNameList, startingNumber, group, outputDataRootPath, TH, sizeFinder, grippingPoints,
                 classifierClass, gaussianClassifier, calibrationValues):
    """This function is the one executed by the individual processes created in the Trending class. This takes care of
    all the image processing"""
    calibrator = ImageCalibrator()
    ignoreList = [0, 11, 22, 33, 44, 55]
    # goes over all the images allocated to the thread
    for i, fileName in enumerate(indexFileNameList):
        i += startingNumber
        if i not in ignoreList:
            # extract name of image
            name = fileName.rsplit('\\', 1)[-1]
            name = name.split(".")[0]

            print("now processing image:", fileName, name)

            # init data object for the current image
            imageData = ImageData(fileName, i+1, group, )

            # Thresholds image
            TH.isolate(outputDataRootPath, imageData)

            # Calibrates RGB and thresholded image
            calibratedImages = calibrator.calibrateImage(imageData.img, imageData.seperatedThresholdedImage,
                                                         calibrationValues)
            imageData.setCalibratedImages(calibratedImages[0], calibratedImages[1])

            # Runs and saves output from SizeFinder
            imageData.setAtributesFromSizeFinder(sizeFinder.findSize(imageData))
            # Writes Size images and boundingboxes to files
            os.chdir("{}/group_{}/Size/".format(outputDataRootPath, group))
            cv2.imwrite("{} Size Calibrated.png".format(name), imageData.annotatedImage)
            cv2.imwrite("{} OG.png".format(name), imageData.boundingBoxImage)
            cv2.imwrite("{} Size Uncalibrated.png".format(name), imageData.annotatedImageUncalibrated)

            # Classifier starts
            imageData.setAttributesFromGrippingPoints(grippingPoints.calcGrippingPoints(imageData))
            imageData.setZValuesOfPoints(grippingPoints.applyZValues(imageData))
            imageData.setAverageHSV(classifierClass.calculateAverageHSV(imageData))
            imageData.setSpeciesFromClassifier(classifierClass.predictSpecies(gaussianClassifier, imageData))
            
            os.chdir("{}/group_{}/GripPoints/".format(outputDataRootPath, group))
            cv2.imwrite("{} Gripping Points.png".format(name), imageData.grippingPointImage)
        
            # Relevant data is written to a csv file
            os.chdir("{}/group_{}/Results".format(outputDataRootPath, group))
            
            csvHeader = ["group id", "image id", "fish index", "species", "length", "width", "area", "gripping points", "center point", "orientations", "avg hsv", "bounding box"]
            collectedFishOutput = classifierClass.createFishDictionary(imageData)
            with open("result{}.csv".format(str(imageData.index).zfill(5)), "w", newline='') as file:
                csvDictWriter = csv.DictWriter(file, csvHeader)
                csvDictWriter.writeheader()
                csvDictWriter.writerows(collectedFishOutput)



class threading:
    "This Class handles thredding and load balencing"

    def __init__(self, numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, calibrationImages, gausClassifier):
        """Creates the thredding class and creates the processes based on the given params.
        Runs the calibration for the group before distributing the individual images to threads."""
        # Get the calibration values for the group
        calibrator = ImageCalibrator()
        calibrationValues = calibrator.getImageCalibration(calibrationImages)

        # Delete all files in the results folder
        prevoiusResults = glob.glob("{}/group_{}/Results/*".format(outputDataRootPath, group))
        for file in prevoiusResults:
            print("deleting prevous result file:", file)
            os.remove(file)

        # Distributes the images to the threads
        self.process = []
        indexJump = int(math.modf(picturesPerGroup / numberOfThreads)[1])
        optimizeFraction = Fraction(math.modf(picturesPerGroup / numberOfThreads)[0]).limit_denominator(1000000)
        Offset = (numberOfThreads / optimizeFraction.denominator) * optimizeFraction.numerator
        indexOffsetEnd = 0
        indexOffsetStart = 0
        for i in range(numberOfThreads):
            if Offset != 0:
                indexOffsetEnd += 1
                Offset -= 1
            if i == 0:
                if Offset != 0:
                    indexOffsetEnd += 1
                    Offset -= 1
                self.process.append(mp.Process(target=taskHandeler, args=(
                    images[:indexJump + indexOffsetEnd], i, group, outputDataRootPath, Thresholder(), SizeFinder(),
                    GrippingPoints(), Classifier(), gausClassifier, calibrationValues)))
            elif i == numberOfThreads - 1:
                self.process.append(mp.Process(target=taskHandeler, args=(
                    images[i * indexJump + indexOffsetStart:picturesPerGroup + 1], i * indexJump + indexOffsetStart,
                    group,
                    outputDataRootPath, Thresholder(), SizeFinder(), GrippingPoints(), Classifier(), gausClassifier,
                    calibrationValues)))
            else:
                self.process.append(mp.Process(target=taskHandeler, args=(
                    images[i * indexJump + indexOffsetStart:(i + 1) * indexJump + indexOffsetEnd],
                    i * indexJump + indexOffsetStart, group, outputDataRootPath, Thresholder(), SizeFinder(),
                    GrippingPoints(), Classifier(), gausClassifier, calibrationValues)))

    def start(self):
        """Starts the processes initialized in the class"""
        for element in self.process:
            element.start()

        for element in self.process:
            element.join()


def logicHandle(pathInputRoot, groups):
    # For timing the pressings runtime. Not critical for function
    startTime = time.time()
    
    clf = Classifier()
    gaussianClassifer = clf.createClassifier("./Identification/DATAdir/annotations_training_data.csv", "./Identification/DATAdir/annotated_output_testing_data.csv")

    for group in groups:
        ########################################### Setup params ##############################################
        images = glob.glob("{}/group_{}/rs/rgb/*.png".format(pathInputRoot, group))[:45]
        calibrationImages = glob.glob("{}/group_{}/calibration/rs/*.png".format(pathInputRoot, group))
        outputDataRootPath = "C:/P3OutData/Merged"  # where you want the program to create it's data folders (could be defined in GUI TBD)
        numberOfThreads = mp.cpu_count()  # Sets the amount of threads to use to match the threads on the computers CPU
        picturesPerGroup = len(images)
        ########################################### Setup params END #########################################
        pathingSetup(group, outputDataRootPath)
        
        imageDataList = [x for x in range(picturesPerGroup)] # List that containes all the imagData objects of a group

        # An object containing all the threaded image processing tasks
        process = threading(numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, calibrationImages,
                            gaussianClassifer)

        process.start()

    # For timing the prosessings runtime. Not critical for function
    print("TIME:", str(startTime - time.time()))


def logicStart(pathInputRoot, groups):
    logic = mp.Process(target=logicHandle, args=(pathInputRoot, groups))
    logic.start()
