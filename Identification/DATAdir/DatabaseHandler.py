import mysql.connector
from mysql.connector import Error
import random


class Database():
    # Starter en forbindelse til mysql databasen og opretter dictionary der er bruges til tabellen senere.
    def __init__(self, IPAddress, port):
        self.IPAddress = IPAddress
        self.port = port
        self.mysql = mysql.connector.connect(host=self.IPAddress, port=self.port, user="frederik", password="frederik",
                                             database="Ehhhm")
        self.curs = self.mysql.cursor(buffered=True)


    # Reopen the connection to the database
    def connect(self):
        self.mysql.connect()
        return self.mysql.is_connected()

    # CLose the connection to the database
    def close(self):
        self.mysql.close()

    # Udfør en database interaktion og "commit"er den.
    def _do(self, cmd: str, val: tuple = None):
        if val is None:
            self.curs.execute(cmd)
        else:
            self.curs.execute(cmd, val)
        if val != {"nocom": "yeet"}:
            self.mysql.commit()

    # Creates a table with the name of the gameid, with columns for data collected during the ID phase.
    # Each row represents an individual fish.
    def createTable(self, tableName):
        self.curs.execute("SHOW TABLES")
        tables = self.curs.fetchall()
        # If the table does not exist, create it.
        if (tableName,) not in tables:
            self._do("CREATE TABLE {} (ID INT, Species VARCHAR(255), Lenght FLOAT, Orientation1 INT, Orientation2 INT, GripPointsX INT, GripPointsY INT)".format(tableName))
            print("Table created")
        else:
            print("Table already exists")

    def deleteTable(self, tableName):
        """Deletes a table from the database, where tableName is the name of the table"""
        self.curs.execute("DROP TABLE {}".format(tableName))
        print("Table deleted")


    def pull(self, tableName, place, value):
        """Pulls a row from the database, where tableName is the name of the table, place is the column you want to
        pull from"""
        self.curs.execute("SELECT * FROM {} WHERE {} = {}".format(tableName, place, value))
        return self.curs.fetchall()

    def pullRow(self, tableName, row):
        """Pulls a row from a table in the database, where tableName is the name of the table, row is the row you
        want to pull from"""
        self.curs.execute("SELECT * FROM {} WHERE id = {}".format(tableName, row))
        return self.curs.fetchall()

    def pullall(self):
        """Pulls all tables from the database"""
        self.curs.execute("Show tables;")
        return self.curs.fetchall()

    def addFish(self, tableName, fishData):
        """Inserts a new row into a table with the data in the columns. tableName is the name of the table, and fishData
        is a tuple containing the data for the columns"""
        self._do("INSERT INTO {} (ID, Species, Lenght, Orientation1, Orientation2, GripPointsX, GripPointsY) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(tableName), fishData)


