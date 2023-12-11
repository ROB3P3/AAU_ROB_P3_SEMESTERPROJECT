import cv2
import numpy as np
import os


class Cropper:
    """The class wich crops the images on the provided file path (skal måske laves om til at køre på img fra tidligere kode i stedet)"""

    def __init__(self):
        self.img = 0
        self.imgCropped = 0

    def showImage(self, images):
        """Function to show an array of images until 0 is pressed"""
        for i, image in enumerate(images): cv2.imshow("Image" + str(i + 1), image)
        while True:
            k = cv2.waitKey(0) & 0xFF
            if k == 48:
                break
            print(k)

    def setImage(self, image):

        self.imagePlot = image.copy()
        # convert to greyscale if needed
        if len(image.shape) > 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.img = image
        y, x = image.shape
        self.imgCropped = np.zeros((y, x))

    def findEdges(self):
        # self.imgGrey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.imgEdges = cv2.Canny(self.img, 250, 400, apertureSize=3)

    def findVerticalLines(self):
        self.imgLines = self.imagePlot.copy()
        # Finds lines in the image based on edges
        self.Lines = cv2.HoughLines(self.imgEdges, 1.7, np.pi / 180, 220)


        self.minx = 9999
        for r_theta in self.Lines:
            arr = np.array(r_theta[0], dtype=np.float64)
            r, theta = arr

            a = np.cos(theta)  # Stores the value of cos(theta) in a
            b = np.sin(theta)  # Stores the value of sin(theta) in b

            x0 = a * r  # x0 stores the value rcos(theta)
            y0 = b * r  # y0 stores the value rsin(theta)

            x1 = int(x0 + 1200 * (-b))  # x1 stores the rounded off value of (rcos(theta)-1000sin(theta))
            y1 = int(y0 + 1200 * (a))  # y1 stores the rounded off value of (rsin(theta)+1000cos(theta))

            x2 = int(x0 - 1200 * (-b))  # x2 stores the rounded off value of (rcos(theta)+1000sin(theta))
            y2 = int(y0 - 1200 * (a))  # y2 stores the rounded off value of (rsin(theta)-1000cos(theta))

            # cv2.line draws a line in img from the point(x1,y1) to (x2,y2).
            # (0,0,255) denotes the colour of the line to be
            # drawn. In this case, it is red.
            # This if statments only lets approxemetly vertical lines be saved
            if abs(y1 - y2) > 100 > abs(x1 - x2):
                if self.minx > x0 > 550:
                    #self.imgLines = self.imagePlot.copy()
                    self.minx = x0
                    cv2.line(self.imgLines, (x1, y1), (x2, y2), (0, 0, 255), 2)

        #self.showImage([self.imgLines])





    def crop(self):
        # This function executes the corpping and creates and atribute: imgCropped
        self.findEdges()
        self.findVerticalLines()

        # Makes all outside the conveyorbelt black, by looking at ab ankor point found in "find vertical lines": minx
        for y, row in enumerate(self.imgCropped):
            for x, pixel in enumerate(row):
                # +70 to go from the outer edge on the conveyobelt to the eged by the conveyor bed. Found frome trial and error, the same goes for +1200
                if x < self.minx + 70 or x > self.minx + 1220:
                    self.imgCropped[y][x] = 255
        self.xStart = round(self.minx + 70)
        self.xEnd = round(self.minx + 1220)

        # fill the area between the lines with half transparent red
        overlay = self.imagePlot.copy()
        # area is not a rectangle, so we need to define the polygon points
        pts = np.array([[self.xStart, 0], [self.xStart, 1080], [self.xEnd, 1080], [self.xEnd, 0]])
        cv2.fillPoly(overlay, [pts], (255, 0, 0))
        overlay = cv2.addWeighted(overlay, 0.5, self.imagePlot, 0.5, 0)
        self.imagePlot = cv2.addWeighted(overlay, 0.5, self.imagePlot, 0.5, 0)

        self.imagePlot = cv2.line(self.imagePlot, (self.xStart, 0), (self.xStart, 1080), (0, 0, 255), 5)
        self.imagePlot = cv2.line(self.imagePlot, (self.xEnd, 0), (self.xEnd, 1080), (0, 0, 255), 5)
        # export the image to downloads
        #os.chdir(r"C:\Users\klump\Downloads")
        #cv2.imwrite("AutoCropOutput.png", self.imagePlot)
        #self.showImage([self.imagePlot])

        return self.minx


#if __name__ == "__main__":
if False:
    # Test code
    image = cv2.imread(r"C:\FishProject\group_19\rs\rgb\00002.png", cv2.IMREAD_UNCHANGED)
    imageWarp = image.copy()
    imageThreshold = image.copy()
    AutoCropper = Cropper()
    AutoCropper.setImage(image)
    minX = round(AutoCropper.crop())

    leftX1 = minX + 67
    leftX2 = minX + 70
    rightX1 = minX + 1235
    rightX2 = minX + 1270
    if False:
        imageWarp = cv2.line(imageWarp, (leftX1, 0), (leftX2, 1080), (0, 0, 255), 5)
        imageWarp = cv2.line(imageWarp, (rightX1, 0), (rightX2, 1080), (0, 0, 255), 5)
        # fill the area between the lines with half transparent red
        overlay = imageWarp.copy()
        # area is not a rectangle, so we need to define the polygon points
        pts = np.array([[leftX1, 0], [leftX2, 1080], [rightX2, 1080], [rightX1, 0]])
        cv2.fillPoly(overlay, [pts], (0, 0, 255))
        overlay = cv2.addWeighted(overlay, 0.5, imageWarp, 0.5, 0)
        imageWarp = cv2.addWeighted(overlay, 0.5, imageWarp, 0.5, 0)

        imageThreshold = cv2.line(imageThreshold, (leftX1, 0), (leftX1, 1080), (0, 0, 255), 5)
        imageThreshold = cv2.line(imageThreshold, (rightX1, 0), (rightX1, 1080), (0, 0, 255), 5)
        # fill the area between the lines with half transparent red
        overlay = imageThreshold.copy()
        # area is not a rectangle, so we need to define the polygon points
        pts = np.array([[leftX1, 0], [leftX1, 1080], [rightX1, 1080], [rightX1, 0]])
        cv2.fillPoly(overlay, [pts], (0, 0, 255))
        overlay = cv2.addWeighted(overlay, 0.5, imageThreshold, 0.5, 0)
        imageThreshold = cv2.addWeighted(overlay, 0.5, imageThreshold, 0.5, 0)

        # export the image to downloads
        os.chdir(r"C:\Users\klump\Downloads")
        #cv2.imwrite("test.png", image)
        cv2.imshow("warp", imageWarp)
        cv2.imshow("threshold", imageThreshold)
        cv2.waitKey(0)