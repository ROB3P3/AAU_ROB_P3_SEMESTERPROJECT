import cv2
import numpy as np
def rotOfFish(img,extremums,minimum,centerpoint):
        
        img = cv2.imread(img)
        vectorAB=(minimum[0]+extremums[0],minimum[1]+extremums[1])
        # Given 2D vector
        given_vector = np.array([vectorAB[0], vectorAB[1]])

    # Find an orthogonal vector by flipping the vectorAB
        orthogonal_vector = np.array([-given_vector[1], given_vector[0]]) 
        print(orthogonal_vector)
        orthogonalLength=-given_vector[1]**2+given_vector[0]**2
        normalizedVector=[-given_vector[1]/orthogonalLength,given_vector[0]/orthogonalLength]
        print(normalizedVector)
        for cp in centerpoint:
            i = 1
            pixel = 1
            while pixel!=0:
                pixelX=cp[0]+normalizedVector[0]*i
                pixelY=cp[1]+normalizedVector[1]*i
                pixel=threshold[pixelY][pixelX]
                i += 1
                positiveDirection=i

            i = -1
            pixel = 1
            while pixel!=0:
                pixelX=cp[0]+normalizedVector*i
                pixelY=cp[1]+normalizedVector*i
                pixel=threshold[pixelY][pixelX]
                i -= 1
                negativeDirection=i
        Stroke=(positiveDirection*pixelThreshold,negativeDirection*pixelThreshold)
        return Stroke
        

        

  

