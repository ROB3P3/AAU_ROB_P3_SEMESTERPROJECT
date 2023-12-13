import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import pandas as pd
import math
import cv2

class Classifier:
    def __init__(self) -> None:
        print("Classifier initialized")
    
    def createFishDictionary(self, imageData):
        fishOutputDict = []
        for i in range(len(imageData.fishLenghts)):
            print("Fish: ", i+1, " of ", len(imageData.fishLenghts), " in image: ", imageData.imagePath)
            try:
                if i == 0:
                    fishDict = {"group id": imageData.group, "image id": imageData.index, "fish index": i+1, "species": imageData.fishSpecies[i], "length": imageData.fishLenghts[i], "width": imageData.fishWidths[i], "area": imageData.fishAreas[i], "gripping points": imageData.fishGrippingPoints[i], "center point": imageData.averagePoints[i], "orientations": imageData.fishOrientations[i], "avg hsv": imageData.fishAverageHSV[i], "true negatives" : imageData.trueNegatives}
                    fishOutputDict.append(fishDict)
                else:
                    fishDict = {"group id": imageData.group, "image id": imageData.index, "fish index": i + 1,
                                "species": imageData.fishSpecies[i], "length": imageData.fishLenghts[i],
                                "width": imageData.fishWidths[i], "area": imageData.fishAreas[i],
                                "gripping points": imageData.fishGrippingPoints[i],
                                "center point": imageData.averagePoints[i],
                                "orientations": imageData.fishOrientations[i], "avg hsv": imageData.fishAverageHSV[i], "true negatives" : 0}
                    fishOutputDict.append(fishDict)
            except IndexError:
                print("Dictionary IndexError in: ", imageData.imagePath)
                break
        return fishOutputDict
    
    def createFeatures(self, lengthArray, widthArray, areaArray, hsvArray, imageData):
        """Create a list of features for each fish from feature arrays"""
        fishFeatures = []
        for i in range(len(lengthArray)):
            print("Fish: ", i+1, " of ", len(lengthArray), " in image: ", imageData.imagePath)
            try:
                fishData = [lengthArray[i], widthArray[i], hsvArray[i][0], hsvArray[i][1], hsvArray[i][2]]
                fishFeatures.append(fishData)
            except IndexError:
                print("Feature IndexError in: ", imageData.imagePath)
                break
        return fishFeatures
    
    def extractFeatures(self, dataArray):
        """Extract features from csv datasets and return them as numpy arrays for the classifier"""
        species = dataArray["species"].to_numpy()
        
        # Empty array to contain all features per fish
        arr = []
        # An array of fish to remove that have 'NaN' values
        fishToRemove = []
        for i, row in dataArray.iterrows():
            lengthValue = row["length"]
            widthValue = row["width"]
            if math.isnan(lengthValue):
                fishToRemove.append(i)
                continue
            areaValue = row["area"]
            
            hsvArray = row["avg hsv"].replace("[", "").replace("]", "").split(" ")
            while '' in hsvArray:
                hsvArray.remove('')
            
            hueValue = float(hsvArray[0])
            saturationValue = float(hsvArray[1])
            valueValue = float(hsvArray[2])
            fishData = [lengthValue, widthValue, hueValue, saturationValue, valueValue]
            arr.append(fishData)
        arr = np.asarray(arr, dtype=np.float64)
        
        # Remove fish with 'NaN' values from species array
        fishToRemove.sort(reverse=True)
        for i in fishToRemove:
            species = np.delete(species, i)
        
        return arr, species
    
    def createClassifier(self, trainingDataPath, valDataPath):
        """Create a Gaussian Naive Bayes classifier and train it with the training data"""
        trainingData = pd.read_csv(trainingDataPath, usecols = ["species", "length", "width", "area", "avg hsv"])
        valData = pd.read_csv(valDataPath, usecols = ["species", "length", "width", "area", "avg hsv"])
        
        # Create arrays of features and species in same order for training and validation data
        trainFeatureArray, trainSpeciesArray = self.extractFeatures(trainingData)
        valFeatureArray, valSpeciesArray = self.extractFeatures(valData)
        
        # Create and train a Gaussian Naive Bayes classifier
        gausClassifier = GaussianNB()
        gausClassifier.fit(trainFeatureArray, trainSpeciesArray)
        
        # Make predictions on the validation data
        yPrediction = gausClassifier.predict(valFeatureArray)

        # Compute accuracy and f1 score based on ground truth of validation data and prediction
        accuracy = accuracy_score(valSpeciesArray, yPrediction)
        f1 = f1_score(valSpeciesArray, yPrediction, average=None)
        precision = precision_score(valSpeciesArray, yPrediction, average=None)
        recall = recall_score(valSpeciesArray, yPrediction, average=None)
        print("Accuracy:", accuracy)
        print("F1 Score:", f1)
        print("Precision:", precision)
        print("Recall:", recall)
        
        # Uncomment to display confusion matrix
        """ cm = confusion_matrix(valSpeciesArray, yPrediction, labels=gausClassifier.classes_)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,display_labels=gausClassifier.classes_)
        disp.plot()
        plt.show() """
        
        return gausClassifier

    def calculateAverageHSV(self, imageData):
        """Calculate the average HSV value of each fish by using the contours of the fish"""
        image = imageData.img
        fishContours = imageData.separateContours
        
        fishAverageHSV = []
        for contour in fishContours:
            # Create an empty image with only the individual contour
            indContourImage = np.zeros(image.shape, dtype=np.uint8)
            cv2.drawContours(indContourImage, contour, -1, (255, 255, 255), -1)
            # Count every non-black pixel in the image
            yPixels, xPixels, zPixels = np.nonzero(indContourImage)
            
            # Convert to HSV and calculate the average HSV value by finding the mean value using the pixels from the contour
            hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            avgColorHSV = np.mean(hsvImage[yPixels, xPixels], axis=0)
            fishAverageHSV.append(avgColorHSV)
        return fishAverageHSV

    def predictSpecies(self, classifier, imageData):
        """Predict the species of a fish based on its features"""
        fishFeatures = self.createFeatures(imageData.fishLenghts, imageData.fishWidths, imageData.fishAreas, imageData.fishAverageHSV, imageData)
        prediction = classifier.predict(fishFeatures)
        return prediction
