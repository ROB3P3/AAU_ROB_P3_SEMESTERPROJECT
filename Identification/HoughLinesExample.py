import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import cv2
import time
import LOGIKdir.AutoCrop as AutoCrop
import math

def plotData(data, title, xLabel, yLabel, savePath, saveName):
    """Plot a scatterplot of the data"""
    plt.scatter(data[0], data[1])
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.savefig("{}/{}.png".format(savePath, saveName))
    plt.clf()


if __name__ == "__main__":
    image = cv2.imread(r"C:\Users\klump\Downloads\HoughLinesSample2.png", cv2.IMREAD_GRAYSCALE)

    cropper = AutoCrop.Cropper()
    cropper.setImage(image)
    edges = cropper.findEdges()
    cropper.findVerticalLines()

    # get a list of all the coordinates of the white pixels in the image
    rhoInput = 1
    coordinates = np.where(image == 255)
    print("coordinates: ", len(coordinates))
    # print the maximum x and y coordinates
    print("x: ", np.max(coordinates[1]), "y: ", np.max(coordinates[0]))
    print(len(coordinates[0]), len(coordinates[1]))

    # lenght of the diagonal of the image
    diagonal = math.floor(np.sqrt(1920 ** 2 + 1080 ** 2))
    print("diagonal: ", diagonal)

    # Prepare the formula: rho=x*cos(theta)+y*sin(theta) for a 1920x1080 image.
    rho = np.linspace(-diagonal, diagonal, math.floor((diagonal/rhoInput)*2), dtype=int)
    theta = np.linspace(-np.pi, np.pi, 180, dtype=np.int64)
    thetaGrid, rhoGrid = np.meshgrid(theta, rho)
    # prepare a list x and y coordinates to calculate the hough transform

    print(len(theta))
    print(len(rho))

    print("Rho range:", rho[1250:1270])



    time1 = time.time()
    # calculate the hough transform for each x and y coordinate and vote for the corresponding rho and theta.
    hough = np.zeros((len(rho), len(theta)), dtype=np.int64)
    for i in range(len(coordinates[0])):
        x = coordinates[1][i]
        y = coordinates[0][i]
        for j in range(len(theta)):
            # calculate the rho for the current theta
            rhoCalc = x * np.cos(theta[j]202) + y * np.sin(theta[j])
            if theta[j] < 0:
                rhoCalc = -rhoCalc
            # find the closest rho in the rho array
            rhoIndex = np.where(rho == math.floor(rhoCalc))[0][0]
            # vote for the rho and theta
            hough[rhoIndex][j] += 1


    print("Time: ", time.time() - time1)
    # plot the hough transform and stretch the theta axis to match the rho axis. the colorbar shows the amount of votes, where
    # the brightest color is the maximum votes any paramter recieved.
    plt.imshow(hough, aspect='auto', extent=[0, 180, -diagonal, diagonal])
    plt.xlabel("Theta")
    plt.ylabel("Rho")

    # show what the colorbar.
    plt.colorbar()

    #plt.title("Hough Transform without threshold")
    # save the image
    plt.savefig(r"C:\Users\klump\Downloads\HoughTransformNoThreshold.png")

    plt.show()


    print("Hough transform with threshold")

    # plot the hough transform with a threshold of 220 votes
    plt.imshow(hough > 219, extent=[-180, 180, 0, diagonal], aspect='auto')
    plt.xlabel("Theta")
    plt.ylabel("Rho")
    plt.colorbar()
    plt.title("Hough Transform with threshold")
    plt.savefig(r"C:\Users\klump\Downloads\HoughTransformWithThreshold.png")

    #plt.show()


