import glob
import os
import pandas as pd





if __name__ == "__main__":
    speciesCSV = glob.glob(r"C:\P3OutData\Merged\group_19\Results corrected\*.csv")

    correctedCSV = glob.glob(r"C:\FishProject\18-25\group_19\Results\*.csv")
    # get the number from the corrected CSV file name.
    for CSV in correctedCSV:
        name = CSV.split("\\")[-1]
        name = name.split(".")[0]
        # split the number from the name so result10 becomes 10
        name = name.split("result")[1]
        name = name.zfill(5)
        print("result" + name + ".csv")
        # rename the file to the number
        os.rename(CSV, r"C:/FishProject/18-25/group_19/Results/result{}.csv".format(name))

    correctedCSV = glob.glob(r"C:\FishProject\18-25\group_19\Results\*.csv")
    for i, CSV in enumerate(correctedCSV):
        print(CSV)
        corrected = pd.read_csv(CSV)
        species = pd.read_csv(speciesCSV[i])
        print("before corrected: \n", corrected["species"])
        print("correct species: \n", species["species"])
        corrected["species"] = species["species"]
        print("after corrected: \n", corrected["species"])
        corrected.to_csv(CSV, header=True, index=False)
