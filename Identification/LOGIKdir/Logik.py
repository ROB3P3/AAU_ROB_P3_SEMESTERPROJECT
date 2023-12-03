import cv2
import numpy as np
import math
import os
import multiprocessing as mp
from fractions import Fraction
from LOGIKdir.Sizefinder import SizeFinder
from LOGIKdir.IsolatingFish2 import Thresholder
from DATAdir.data import ImageData
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

def taskHandeler(indexFileNameList, startingNumber, group, outputDataRootPath, TH, sizeFinder, imageDataList):
    "This function is the one executed by the indeidual processes created in the Tredding class"
    for i, fileName in enumerate(indexFileNameList):
            i += startingNumber

            print("now processing image:", fileName)

            imageData = ImageData(fileName,i+1, group,)

            TH.isolate(outputDataRootPath, imageData)

            imageData.setAtributesFromSizeFinder(sizeFinder.findSize(imageData))
            
            os.chdir("{}/group_{}/Size".format(outputDataRootPath, group))
            cv2.imwrite("size"+str(i+1)+".png",imageData.annotatedImage)
            cv2.imwrite("OG"+str(i+1)+".png",imageData.boundingBoxImage)
            imageDataList[i-1] = imageData.boundingBoxImage

class thredding:
    "This Class handles thredding and load balencing"
    def __init__(self, numberOfThreads,images ,picturesPerGroup, group, outputDataRootPath, imageDataList):
        "Creates the thredding class and creates the processes based on the given params"
        self.process = []
        indexJump = int(math.modf(picturesPerGroup/numberOfThreads)[1])
        optimizeFraction = Fraction(math.modf(picturesPerGroup/numberOfThreads)[0]).limit_denominator(1000000)
        Offset = (numberOfThreads/optimizeFraction.denominator)*optimizeFraction.numerator
        indexOffsetEnd = 0
        indexOffsetStart = 0
        for i in range(numberOfThreads):
            if Offset != 0:
                indexOffsetEnd +=1
                Offset -= 1
            if i == 0:
                if Offset != 0:
                    indexOffsetEnd +=1
                    Offset -= 1
                self.process.append(mp.Process(target=taskHandeler, args=(images[1:indexJump+indexOffsetEnd],1,group, outputDataRootPath, Thresholder(), SizeFinder(),imageDataList)))
            elif i == numberOfThreads-1:
                self.process.append(mp.Process(target=taskHandeler, args=(images[i*indexJump+indexOffsetStart:picturesPerGroup+1],i*indexJump+indexOffsetStart,group, outputDataRootPath, Thresholder(), SizeFinder(),imageDataList)))
            else:
                self.process.append(mp.Process(target=taskHandeler, args=(images[i*indexJump+indexOffsetStart:(i+1)*indexJump+indexOffsetEnd],i*indexJump+indexOffsetStart,group, outputDataRootPath, Thresholder(), SizeFinder(),imageDataList)))

    def start(self):
        "Starts the processes initialized in the class"
        for element in self.process:
                element.start()

        for element in self.process:
            element.join()
            
def logikStart(pathInputRoot, groups):
    mp.set_start_method("spawn")
    startTime = time.time()
    user = os.environ.get('USERNAME')
    #groups = [10]#[10, 14, 20, 21, 22] # The groups the program is goinf through

    for group in groups:
        ########################################### Setup params ##############################################
        #pathInputRoot = "C:/Users/{}/OneDrive - Aalborg Universitet/autofish_rob3".format(user) # OBS!!!!! Change to directory to Data set ROOT (where the groups are)
        images = glob.glob("{}/group_{}/rs/rgb/*.png".format(pathInputRoot, group)) 
        outputDataRootPath = "C:/P3OutData/Merged" # where you want the program to create it's data folders
        numberOfThreads = mp.cpu_count()-2 # OBS!!!!! chose the amount of threds to use
        picturesPerGroup = len(images)
        ########################################### Setup params END #########################################
        

        pathingSetup(group, outputDataRootPath)
        
        imageDataList = [x for x in range(picturesPerGroup)] # List that containes all the imagData objects of a group

        process = thredding(numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, imageDataList)

        process.start()
    
    print("TIME:", str(startTime-time.time()))