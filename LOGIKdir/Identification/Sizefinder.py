import cv2

imageRGB = cv2.imread(r"DATAdir/RGB/PNG/00004.png")


class FindSize():
    

cv2.imshow("RGB", imageRGB)
cv2.waitKey(0)