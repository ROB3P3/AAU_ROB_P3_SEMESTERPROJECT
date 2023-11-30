import time
import glob
from LOGIKdir.Logik import *

if __name__ == "__main__":
    startTime = time.time()
    user = os.environ.get('USERNAME')
    groups = [10]#[10, 14, 20, 21, 22] # The groups the program is goinf through

    for group in groups:
        ########################################### Setup params ##############################################
        pathInputRoot = "C:/Users/{}/OneDrive - Aalborg Universitet/autofish_rob3".format(user) # OBS!!!!! Change to directory to Data set ROOT (where the groups are)
        images = glob.glob("{}/group_{}/rs/rgb/*.png".format(pathInputRoot, group)) 
        outputDataRootPath = "C:/P3OutData/Merged" # where you want the program to create it's data folders
        numberOfThreads = 4 # OBS!!!!! chose the amount of threds to use
        picturesPerGroup = 66
        ########################################### Setup params END #########################################
        

        pathingSetup(group, outputDataRootPath)
        
        imageDataList = [x for x in range(picturesPerGroup)] # List that containes all the imagData objects of a group

        process = thredding(numberOfThreads, images, picturesPerGroup, group, outputDataRootPath, imageDataList)

        process.start()
    
    print("TIME:", str(startTime-time.time()))