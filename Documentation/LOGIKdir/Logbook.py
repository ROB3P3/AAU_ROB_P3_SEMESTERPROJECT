import Documentation.DATAdir.DatabaseHandler as DatabaseHandler


class LogbookCompiler:
    def __init__(self):
        self.tableName = None
        self.Database = None
        self.logbook = []
        # create a dictionary with the minimum lenght of each species from the database.
        self.minimumLenghtDict = {"Salmon": 30, "Tuna": 40, "Macrel": 10, "Cod": 30, "Trout": 10, "Haddock": 25}
        self.fishAmountBMS = {"Salmon": 0, "Tuna": 0, "Macrel": 0, "Cod": 0, "Trout": 0, "Haddock": 0}
        self.fishAmountNormal = {"Salmon": 0, "Tuna": 0, "Macrel": 0, "Cod": 0, "Trout": 0, "Haddock": 0}
        self.fishSpecies = ["Salmon", "Tuna", "Macrel", "Cod", "Trout", "Haddock"]

    def compile(self, IPAdress, port, tableName):
        """Compiles the logbook"""
        self.Database = DatabaseHandler.Database(IPAdress, port)
        self.tableName = tableName


        # Go through each row in the table and compare the lenght of the fish to the minimum lenght of the species in the minimumLenghtDict.
        # If the fish above the lenght, count it in fishAmountNormal.
        # If it is below the lenght, count it in fishAmountBMS.
        for i in range(self.Database.pullRowAmount(self.tableName)):
            fishSpecies, fishLenght,  = self.Database.pullRow(self.tableName, i+1)[1:3]
            print("Fish lenght: {}".format(fishLenght), "Fish species: {}".format(fishSpecies))
            if fishLenght >= self.minimumLenghtDict[fishSpecies]:
                self.fishAmountNormal[fishSpecies] += 1
            else:
                self.fishAmountBMS[fishSpecies] += 1

        print("FishAmountNormal: {}".format(self.fishAmountNormal), "FishAmountBMS: {}".format(self.fishAmountBMS))
        self.fishCount = [self.fishAmountNormal, self.fishAmountBMS]
        self.logbook.append(self.fishCount)
        return self.logbook
