import cv2
import os
import glob

def findEdge(image):
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    imageGraBlur = cv2.medianBlur(imageGray,7)

    imageEdgeBlur = cv2.Canny(imageGraBlur,90,190)

    element = cv2.getStructuringElement(1, (2 * 2 + 1, 2 * 2 + 1),
                                        (2, 2))
    imageEdgeBlurDilated = cv2.dilate(imageEdgeBlur,element)

    return imageEdgeBlurDilated

#Dette er hvor filen fra oenstående funktion bliver gemt, dette er ikke nødvendigt i den færdie implementation af det fulde program, men blve brugt i dne hardkodede version
for i in range(66):
    i += 1
    print(i)
    if i < 10:
        image = cv2.imread("C:/Users/fhp89/OneDrive - Aalborg Universitet/autofish_rob3/group_4/rs/rgb/0000" + str(i) + ".png")
        os.chdir("D:/P3DATA/Edges")
        cv2.imwrite("0000"+str(i)+"Edge.png", findEdge(image))
    else:
        image = cv2.imread("C:/Users/fhp89/OneDrive - Aalborg Universitet/autofish_rob3/group_4/rs/rgb/000" + str(i) + ".png")
        os.chdir("D:/P3DATA/Edges")
        cv2.imwrite("000"+str(i)+"Edge.png", findEdge(image))

def seperate(imageT, imageE):
    image = cv2.subtract(imageT,imageE)

    element = cv2.getStructuringElement(1, (2 * 1 + 1, 2 * 1 + 1),
                                            (1, 1))
    imageErode = cv2.erode(image,element)

    contour = cv2.findContours(imageErode,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)[0]

    for cnt in contour:
        cv2.drawContours(imageErode,[cnt],0,255,-2)
    return imageErode

os.chdir("D:/P3DATA/Edges")
i=0
for i in range(0): # var 65
    i += 2
    print(i)
    if i < 10:
        imageT = cv2.imread("0000{}Th.png".format(i),cv2.IMREAD_GRAYSCALE)
        imageE = cv2.imread("0000"+str(i)+"Edge.png",cv2.IMREAD_GRAYSCALE)
        os.chdir("D:/P3DataOut/group_4")
        cv2.imwrite("0000"+str(i)+"Final.png", seperate(imageT,imageE))
    else:
        imageT = cv2.imread("0000{}Th.png".format(i),cv2.IMREAD_GRAYSCALE)
        imageE = cv2.imread("000"+str(i)+"Edge.png",cv2.IMREAD_GRAYSCALE)
        os.chdir("D:/P3DataOut/group_4")
        cv2.imwrite("000"+str(i)+"Final.png", seperate(imageT,imageE))


