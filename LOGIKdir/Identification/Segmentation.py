import cv2

class FishSegmentation():
    def loadImage(self, path):
        """Loads image from path as RGB and HSV"""
        # Load image as RGB
        self.imageRGB = cv2.imread(path)
        # Convert image to HSV color space
        self.imageHSV = cv2.cvtColor(self.imageRGB, cv2.COLOR_BGR2HSV)


    def showImage(self):
        cv2.imshow("RGB", self.imageRGB)
        cv2.imshow("HSV", self.imageHSV)
        cv2.waitKey(0)


path = r"DATAdir/RGB/tiff/00016.tiff"
# path = r"DATAdir/RGB/PNG/00004.png"
segmenetation = FishSegmentation()
segmenetation.sh(path)
