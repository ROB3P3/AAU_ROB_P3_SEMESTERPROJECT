import Documentation.DATAdir.DatabaseHandler as DatabaseHandler


class LogbookCompiler:
    def __init__(self):
        self.tableNameList = []
        self.Database = None
        self.logbook = []
        # create a dictionary with the minimum lenght of each species from the database.
        self.minimumLenghtDict = {"Hake": 27, "Cod": 35, "Haddock": 30, "Whiting": 27, "Saithe": 35,
                                  "Horse mackerel": 30,
                                  "*others": 0}
        self.fishAmountBMS = {"Hake": 0, "Cod": 0, "Haddock": 0, "Whiting": 0, "Saithe": 0, "Horse mackerel": 0,
                              "*others": 0}
        self.fishAmountNormal = {"Hake": 0, "Cod": 0, "Haddock": 0, "Whiting": 0, "Saithe": 0, "Horse mackerel": 0,
                                 "*others": 0}
        self.fishSpecies = ['Hake', 'Cod', 'Haddock', 'Whiting', 'Saithe', 'Horse mackerel', '*others']

    def compile(self, IPAdress, port, tableNameList):
        """Compiles the logbook. Takes the IP Address and port of the mySQL server and a list of tables to go through."""
        self.Database = DatabaseHandler.Database(IPAdress, port)
        self.tableNameList = tableNameList

        # Go through each row in the table and compare the lenght of the fish to the minimum lenght of the species in the minimumLenghtDict.
        # If the fish above the lenght, count it in fishAmountNormal.
        # If it is below the lenght, count it in fishAmountBMS.
        for tableName in self.tableNameList:
            print("tableName: {}".format(tableName[0]))
            for i in range(self.Database.pullRowAmount(tableName[0])):
                fishSpecies, fishLenght, = self.Database.pullRow(tableName[0], i + 1)[1:3]
                print("Fish lenght: {}".format(fishLenght), "Fish species: {}".format(fishSpecies))
                if fishLenght >= self.minimumLenghtDict[fishSpecies]:
                    self.fishAmountNormal[fishSpecies] += 1
                else:
                    self.fishAmountBMS[fishSpecies] += 1

            # Append the fishAmountNormal and fishAmountBMS to the logbook, for each table.
            fishCount = [self.fishAmountNormal, self.fishAmountBMS]
            self.logbook.append(fishCount)
        print(self.logbook)
        return self.logbook
