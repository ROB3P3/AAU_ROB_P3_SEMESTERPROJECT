import cv2
import numpy as np


class Cropper:
    """The class wich crops the images on the provided file path (skal måske laves om til at køre på img fra tidligere kode i stedet)"""

    def __init__(self):
        self.img = 0
        self.imgCropped = 0

    def setImage(self, image):
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
        self.imgLines = self.img
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
            if abs(y1 - y2) > 100 and abs(x1 - x2) < 100:
                if x0 < self.minx and x0 > 550:
                    self.minx = x0
                    cv2.line(self.imgLines, (x1, y1), (x2, y2), (0, 0, 255), 2)

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
        self.xStart = self.minx + 70
        self.xEnd = self.minx + 1220
        return self.minx
