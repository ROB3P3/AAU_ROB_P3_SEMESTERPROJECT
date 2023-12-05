import cv2
import numpy as np
import math
import os
import multiprocessing as mp
from fractions import Fraction
from LOGIKdir.Sizefinder import SizeFinder
from LOGIKdir.IsolatingFish2 import Thresholder
from DATAdir.data import ImageData
from LOGIKdir.CameraCalibration import ImageCalibrator
import time
import glob


def pathingSetup(group, rootPath):
    "Formats the file setup the program need. Run this before any of the image processing"
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
    if not os.path.exists("{}/group_{}/Results".format(rootPath, group)):
        os.makedirs("{}/group_{}/Results".format(rootPath, group))


def taskHandeler(indexFileNameList, startingNumber, group, outputDataRootPath, TH, sizeFinder, calibrationValues):
    "This function is the one executed by the indeidual processes created in the Tredding class. This takes care of all the image prosessing"
    calibrator = ImageCalibrator()
    for i, fileName in enumerate(indexFileNameList):
        i += startingNumber
        # goes over all the images allocated to the thread

        print("now processing image:", fileName)

        # init data object for the current image
        imageData = ImageData(fileName, i + 1, group, )

        # Thresholds image
        TH.isolate(outputDataRootPath, imageData)

        # Calibrates RGB and thresholded image
        #calibratedImages = calibrator.calibrateImage(imageData.img, imageData.filledThresholdedImage, calibrationValues)
        #imageData.setCalibratedImages()

        # Runs and saves output from SizeFinder
        imageData.setAtributesFromSizeFinder(sizeFinder.findSize(imageData))

        # Writes Size images and boundingboxes to files
        os.chdir("{}/group_{}/Size".format(outputDataRootPath, group))
        cv2.imwrite("size" + str(i + 1) + ".png", imageData.annotatedImage)
        cv2.imwrite("OG" + str(i + 1) + ".png", imageData.boundingBoxImage)

        # Writes realevant data for MySql comunication to txt file for future reference
        os.chdir("{}/group_{}/Results".format(outputDataRootPath, group))
        f = open("result{}.txt".format(startingNumber), "a")
        f.write(str(imageData.index))
        f.write("\n")
        f.close


class thredding:
    "This Class handles thredding and load balencing"

    def __init__(self, numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, calibrationImages):
        """Creates the thredding class and creates the processes based on the given params.
        Runs the calibration for the group before distributing the individual images to threads."""
        # Get the calibration values for the group
        calibrator = ImageCalibrator()
        calibrationValues = calibrator.getImageCalibration(calibrationImages)

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
                images[1:indexJump + indexOffsetEnd], 1, group, outputDataRootPath, Thresholder(), SizeFinder(),calibrationValues)))
            elif i == numberOfThreads - 1:
                self.process.append(mp.Process(target=taskHandeler, args=(
                images[i * indexJump + indexOffsetStart:picturesPerGroup + 1], i * indexJump + indexOffsetStart, group,
                outputDataRootPath, Thresholder(), SizeFinder(),calibrationValues)))
            else:
                self.process.append(mp.Process(target=taskHandeler, args=(
                images[i * indexJump + indexOffsetStart:(i + 1) * indexJump + indexOffsetEnd],
                i * indexJump + indexOffsetStart, group, outputDataRootPath, Thresholder(), SizeFinder(),calibrationValues)))

    def start(self):
        "Starts the processes initialized in the class"
        for element in self.process:
            element.start()

        for element in self.process:
            element.join()


def logikHandle(pathInputRoot, groups):
    # For timing the prosessings runtime. Not critical for function
    startTime = time.time()

    for group in groups:
        ########################################### Setup params ##############################################
        images = glob.glob("{}/group_{}/rs/rgb/*.png".format(pathInputRoot, group))
        calibrationImages = glob.glob("{}/group_{}/calibration/rs/*.png".format(pathInputRoot, group))
        outputDataRootPath = "C:/P3OutData/Merged"  # where you want the program to create it's data folders (could be defined in GUI TBD)
        numberOfThreads = mp.cpu_count()  # Sets the amount of threads to use to match the threads on the computers CPU
        picturesPerGroup = len(images)
        ########################################### Setup params END #########################################
        

        pathingSetup(group, outputDataRootPath)
        
        imageDataList = [x for x in range(picturesPerGroup)] # List that containes all the imagData objects of a group

        # An object containing all the threadded image prosessing tasks
        process = thredding(numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, calibrationImages)

        process.start()

    # For timing the prosessings runtime. Not critical for function
    print("TIME:", str(startTime - time.time()))


def logikStart(pathInputRoot, groups):
    logik = mp.Process(target=logikHandle, args=(pathInputRoot, groups))
    logik.start()