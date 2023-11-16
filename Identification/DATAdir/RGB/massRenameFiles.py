import os
import cv2
import glob



images = glob.glob(r'DATAdir\RGB\**\CalibrationPNG\*.png', recursive=True)

for i, fileName in enumerate(images):
    print(fileName)
    image = cv2.imread(fileName)
    xLeftTop = 666
    xRightBot = 1870
    image = image[0:1080, xLeftTop:xRightBot]
    newFileName = r"DATAdir/RGB/Calibration/" + str(i+1).zfill(5) + ".png"
    print("Newname: ", newFileName)
    cv2.imwrite(newFileName, image)


