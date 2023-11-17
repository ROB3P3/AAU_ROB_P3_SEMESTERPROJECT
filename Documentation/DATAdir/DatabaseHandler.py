import mysql.connector
import random

class Database:
    # Starter en forbindelse til mysql databasen og opretter dictionary der er bruges til tabellen senere.
    def __init__(self):
        self.mysql = mysql.connector.connect(host="172.26.51.10", user="Villiam", password="Villiam", database="test")
        self.curs = self.mysql.cursor(buffered=True)
        self.dict = {
            "Ycor": 0,
            "A": 1,
            "B": 2,
            "C": 3,
            "D": 4,
            "E": 5,
            "F": 6,
            "G": 7,
            "H": 8,
            "I": 9,
            "J": 10,
            "turn": 11,
        }
    # Udfør en database interaktion og "commit"er den.
    def _do(self, cmd: str, val: tuple = None):
        if val is None:
            self.curs.execute(cmd)
        else:
            self.curs.execute(cmd, val)
        if val != {"nocom": "yeet"}:
            self.mysql.commit()

    # Tilføjer en tabel som er 12x10, hvor 2-11 er spillerpladen, 1 er y koordinat og 12 er til at se om den skal videre
    def start(self, gameid):
        self.gamid = gameid
        self.curs.execute("SHOW TABLES")
        tables = self.curs.fetchall()
        print(tables)
        if (self.gamid,) not in tables:
            self.curs.execute(
                "CREATE TABLE {} (Ycor VARCHAR(255),A VARCHAR(255), B VARCHAR(255),C VARCHAR(255), D VARCHAR(255),E VARCHAR(255), F VARCHAR(255),G VARCHAR(255), H VARCHAR(255),I VARCHAR(255), J VARCHAR(255), turn VARCHAR(255))".format(
                    gameid))

        test = 1
        for i in range(10):
            add = "INSERT INTO {} (Ycor, A, B, C, D,E, F,G, H,I, J, turn) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                gameid)
            val = (test, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            self._do(add, val)
            test += 1

    # Sletter en række fra tabellen, her kan du vælge hvilken data i rækken du søger efter med place variablen
    def delete(self, gameid):
        gameid1 = "{}p1".format(gameid)
        if (gameid1,) in self.pullall():
            print("Deleting p1")
            delete = "DROP TABLE {}"
            self._do(delete.format(gameid1))
        gameid2 = "{}p2".format(gameid)
        if (gameid2,) in self.pullall():
            print("Deleting p2")
            delete = "DROP TABLE {}"
            self._do(delete.format(gameid2))

    # Henter en række fra tabellen, her kan du vælge hvilken data i rækken du søger efter med place variablen
    def pull(self, gameid, hvad: str, ting: str = "Ycor"):
        pull = "SELECT * FROM {}".format(gameid)
        self._do(pull.format(name=ting), {"nocom": "yeet"})
        row = self.curs.fetchone()
        while row is not None:
            if row[self.dict.get(ting)] == hvad:
                return row
            else:
                row = self.curs.fetchone()

    # Henter alle tabeller
    def pullall(self):
        self.curs.execute("Show tables;")
        myresult = self.curs.fetchall()
        return myresult

    # Ændre en værdi i en bestemt række.
    # Er data'en du søger efter.
    # replace er det som du godt vil ændre den gamle værdi til.
    # whatchange bestemmer hvilken værdi i rækken du ændre.
    # whatchange er x, search er y, og replace er ny værdi
    def modify(self, gameid, search: str, replace: str, whatchange: str):
        modify = "UPDATE {id} SET {change} = '{replace}' WHERE Ycor = '{search}'"
        print("Modify:", modify.format(id=gameid, change=whatchange, replace=replace, search=search))
        self._do(modify.format(id=gameid, change=whatchange, replace=replace, search=search))

    # Lukker forbindelsen til databasen
    def close(self):
        self.mysql.close()

    # Genåbner forbindelsen til databasen
    def connect(self):
        self.mysql.connect()


def test():
    makeid = random.randint(0, 999)
    gameidp1 = "P1ID{}".format(makeid)
    gameidp2 = "P2ID{}".format(makeid)
    db = Database()
    db.start(gameidp1)
    db.start(gameidp2)
    print(gameidp1)


def testdelete(gamid):
    db = Database()
    db.delete(gamid)


while True:
    print("Hvad vil du?\n"
          "1: Tilføj\n"
          "2: Ændrer\n"
          "3: Slet\n"
          "4: Se alle")
    valg = int(input())
    if valg == 1:
        test()
    elif valg == 2:
        print("Id:")
        gamid = str(input())
        print("Ycor:")
        Ycor = str(input())
        print("Xcor:")
        column = str(input())
        print("newval:")
        newval = str(input())
        db = Database()
        db.modify(gamid, Ycor, newval, column)
    elif valg == 3:
        print("Gamid:")
        gamid = str(input())
        testdelete(gamid)
    elif valg == 4:
        db = Database()
        print(db.pullall())
    else:
        print("vælg mellem 1 og 4")
