import glob

import pandas as pd


class ReadCSV:
    def __init__(self) -> None:
        print("ReadCSV initialized")

    def readCSV(self, path):
        """Read a csv file and return it as a pandas dataframe"""
        return pd.read_csv(path)

    def readCSVs(self, paths):
        """Read a list of csv files and return them as a list of pandas dataframes"""
        dataframes = []
        for path in paths:
            dataframes.append(self.readCSV(path))
        return dataframes

    def readCSVsAsDict(self, paths):
        """Read a list of csv files and return them as a dictionary of pandas dataframes"""
        dataframes = {}
        for path in paths:
            dataframes[path] = self.readCSV(path)
        return dataframes

    def readCSVsAsDictWithNames(self, paths, names):
        """Read a list of csv files and return them as a dictionary of pandas dataframes with names"""
        dataframes = {}
        for i in range(len(paths)):
            dataframes[names[i]] = self.readCSV(paths[i])
        return dataframes

    def readCSVsAsDictWithNamesAndGroups(self, paths, names, groups):
        """Read a list of csv files and return them as a dictionary of pandas dataframes with names and groups"""
        dataframes = {}
        for i in range(len(paths)):
            dataframes[names[i]] = self.readCSV(paths[i])
            dataframes[names[i]]["group"] = groups[i]
        return dataframes

    def readCSVsAsDictWithNamesGroupsAndIndexes(self, paths, names, groups, indexes):
        """Read a list of csv files and return them as a dictionary of pandas dataframes with names, groups and indexes"""
        dataframes = {}
        for i in range(len(paths)):
            dataframes[names[i]] = self.readCSV(paths[i])
            dataframes[names[i]]["group"] = groups[i]
            dataframes[names[i]]["index"] = indexes[i]
        return dataframes

    def readCSVsAsDictWithNamesGroupsIndexesAndSpecies(self, paths, names, groups, indexes, species):
        """Read a list of csv files and return them as a dictionary of pandas dataframes with names, groups, indexes and species"""
        dataframes = {}
        for i in range(len(paths)):
            dataframes[names[i]] = self.readCSV(paths[i])


if __name__ == "__main__":
    readCSV = ReadCSV()
    CSVs = glob.glob(r"C:\P3OutData\Merged\group_18\Results corrected\*")
    for CSV in CSVs:
        print(CSV)
        df = readCSV.readCSV(CSV)
        print(df)
