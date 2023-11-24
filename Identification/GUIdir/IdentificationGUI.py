import glob
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Label as ttkLabel
from mysql.connector.errors import Error, Warning
from mysql.connector import errorcode
import Identification.DATAdir.DatabaseHandler as DatabaseHandler
import os


class Main(Tk):
    def __init__(self):
        Tk.__init__(self)
        # the container is where we'll stack the frames on top of each other, then select the one we want visible
        # to be raised above the others
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for page in (StartPage, PageOne, PageTwo):
            page_name = page.__name__
            frame = page(parent=container, controller=self)
            self.frames[page_name] = frame
            # put all of the pages in the same location the one on the top of the stacking order will be the one that
            # is visible.
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        if page_name == "StartPage":
            self.title("Identification: Main Menu")
            self.geometry("1000x800")
        elif page_name == "PageOne":
            self.title("Identification: Select groups to identify")
            self.geometry("1000x800")
        elif page_name == "PageTwo":
            self.title("Identification: Showing Progess...")
            self.geometry("1000x800")
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(Frame):
    """what is shown when starting the program. Users will input database, path, and number of groups to identify."""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="royalblue2")

        self.Database = None
        self.isConnected = False
        self.pathValid = False
        self.path = None
        self.groupFolders = []
        self.groupAmount = len(self.groupFolders)
        self.pathReady = False
        self.connectionReady = False
        self.tableName = "table_1"

        # check if entry fields have been modified since last check
        # to prevents user from validating one oath and then changing the path without validating again.
        self.modifiedEntry = False

        self.titleText = Label(self, font=("Arial", "40"), text="Fish Identification", bg="royalblue2",
                               fg="black").place(relx=0.5, rely=0.10, anchor=CENTER)
        self.startButton = Button(self, text="Start", command=lambda: self.start(),
                                  font=("Arial", "25"), bg="black", fg="white").place(relx=0.5, rely=0.75,
                                                                                      anchor=CENTER)
        self.quitButton = Button(self, text="Exit", command=exit, font=("Arial", "20"), bg="black", fg="white").place(
            relx=0.5, rely=0.90, anchor=CENTER)

        # Label underneath connectButton to indicate isConnected, change when connectButton is pressed.
        self.connectionLabel = Label(self, font=("Arial", "15"), text="Not connected", bg="royalblue2", fg="black")
        self.connectionLabel.place(relx=0.8, rely=0.26, anchor=CENTER)

        # Label underneath pathButton to indicate isConnected, change when pathButton is pressed.
        self.pathLabel = Label(self, font=("Arial", "15"), text="Not valid", bg="royalblue2", fg="black")
        self.pathLabel.place(relx=0.85, rely=0.46, anchor=CENTER)

        # label underneath pathField to indicate status of path
        self.pathStatus = Label(self, font=("Arial", "15"), text="Enter path", bg="royalblue2", fg="black")
        self.pathStatus.place(relx=0.5, rely=0.46, anchor=CENTER)

        # port and IP text variable which will be actively validated in checkPortInput()
        self.IPValue = StringVar()
        self.IPValue.trace('w', self.checkIPInput)
        self.portValue = StringVar()
        self.portValue.trace('w', self.checkPortInput)

        # IP address, port, and check
        self.IPField = Entry(self, font=("Arial", "25"), width=15, bg="white", fg="black", justify='center',
                             textvariable=self.IPValue)
        self.IPField.place(relx=0.3, rely=0.20, anchor=CENTER)
        self.IPField.insert(tk.END, "172.26.51.10")
        self.portField = Entry(self, font=("Arial", "25"), width=6, bg="white", fg="black", justify='center',
                               textvariable=self.portValue)
        self.portField.place(relx=0.6, rely=0.20, anchor=CENTER)
        # insert test port
        self.portField.insert(tk.END, "3306")
        self.connectButton = Button(self, text="Connect", command=lambda: self.checkConnection(), font=("Arial", "20"),
                                    bg="black", fg="white")
        self.connectButton.place(relx=0.8, rely=0.2, anchor=CENTER)

        # Path address and check
        self.pathValue = StringVar()
        self.pathValue.trace('w', self.checkPathInput)
        self.pathField = Entry(self, font=("Arial", "25"), width=30, bg="white", fg="black",
                               textvariable=self.pathValue)
        self.pathField.place(relx=0.5, rely=0.40, anchor=CENTER)
        # insert test path
        self.pathField.insert(tk.END, r"C:\FishProject")
        self.pathButton = Button(self, text="Check", command=lambda: self.checkPath(), font=("Arial", "20"), bg="black",
                                 fg="white")
        self.pathButton.place(relx=0.85, rely=0.4, anchor=CENTER)

        # Labels to indicate function of widget
        self.IPlabel = Label(self, font=("Arial", "25"), text="IP:", bg="royalblue2", fg="black")
        self.IPlabel.place(relx=0.15, rely=0.20, anchor=CENTER)
        self.portlabel = Label(self, font=("Arial", "25"), text="Port:", bg="royalblue2", fg="black")
        self.portlabel.place(relx=0.5, rely=0.20, anchor=CENTER)
        self.pathlabel = Button(self, font=("Arial", "25"), text="Path to root:", bg="royalblue2", fg="black",
                                command=lambda: self.askForPath())
        self.pathlabel.place(relx=0.11, rely=0.4, anchor=CENTER)

    def checkPathInput(self, *args):
        """Reacts if pathField has been modified."""
        self.modifiedEntry = True
        self.pathLabel.config(text="Invalid")
        self.pathStatus.config(text="Path modified")
        print("Entry modified? ", self.modifiedEntry)

    def askForPath(self):
        pathAsk = str(tk.filedialog.askdirectory())
        self.modifiedEntry = True
        self.pathStatus.config(text="Invalid")
        self.pathStatus.config(text="Path modified")
        print("Entry modified? ", self.modifiedEntry)
        # clear pathField and insert new path
        self.pathField.delete(0, tk.END)
        self.pathField.insert(tk.END, pathAsk)

    def checkPortInput(self, *args):
        """Check if portField is less than 4 characters and only contains digits."""
        value = self.portValue.get()
        self.modifiedEntry = True
        self.connectionLabel.config(text="Check again")
        print("Entry modified? ", self.modifiedEntry)
        if len(value) > 4:
            self.portValue.set(value[:4])
        elif len(value) < 4:
            for i in range(4 - len(value)):
                value = value + "0"
            self.portValue.set(value)
        if value.isdigit() is False: self.portValue.set(value[:-1])

    def checkIPInput(self, *args):
        """Check if IPField is formatted as a proper IP address."""
        value = self.IPValue.get()
        self.modifiedEntry = True
        self.connectionLabel.config(text="Check again")
        print("Entry modified? ", self.modifiedEntry)
        # check if value is always a digit or a dot.
        for char in value:
            if char.isdigit() is False and char != ".":
                value = value.replace(char, "")
                self.IPValue.set(value)

        # check if value always contains 4 links.
        if len(value.rsplit(".", -1)) > 4:
            self.IPValue.set(value[:-1])
        elif len(value.rsplit(".", -1)) < 4:
            for i in range(4 - len(value.rsplit(".", -1))):
                print(i)
                value = value + "."
                self.IPValue.set(value)

        # check if lenght of each link is less than 4 and value is between 0 and 255.
        splitValue = value.rsplit(".", -1)
        for i, link in enumerate(splitValue):
            if len(link) > 0 and link.isdigit() is True:
                if len(link) > 3 or int(link) > 255:
                    splitValue[i] = link[:-1]
                    value = ".".join(splitValue)
                    self.IPValue.set(value)

    def checkConnection(self):
        """Check if provided IP and port can connect to a mySQL server"""
        IPAdress = str(self.IPField.get())
        port = str(self.portField.get())
        print("IP: {}, Port: {}".format(IPAdress, port))

        # attempt to connect to mySQL database
        try:
            self.Database = DatabaseHandler.Database(IPAdress, port)
            isConnected = self.Database.connect()
            self.connectionLabel.config(text="Connected")
            self.connectionReady = True
            print("Connection is: ", isConnected)
            print(self.Database.pullall())
        except Error as error:
            self.connectionLabel.config(text="Not connected")
            self.connectionReady = False
            print("Error code:", error.errno)  # error number
            print("Error message:", error.msg)  # error message
            print("List of error codes:")
            print(errorcode.CR_CONNECTION_ERROR)
            print(errorcode.CR_CONN_HOST_ERROR)

    def checkPath(self):
        """Check if pathField leads to an existing folder on the local disk."""
        self.path = str(self.pathField.get())
        self.pathReady = False

        print("Path: ", self.path)

        # check if self.path is a folder
        if os.path.isdir(self.path) is True:
            print("All necessary main folders are present")
            # get folders that start with group_
            self.groupFolders = [folder for folder in os.listdir(self.path) if folder.startswith("group_")]

            # if there is at least one group to identify, check if the group contains the necessary files
            self.groupAmount = len(self.groupFolders)
            if self.groupAmount > 0:
                print("There are {} groups to identify".format(self.groupAmount))
                self.pathStatus.config(text="Found {} groups.".format(self.groupAmount))
                self.checkForFiles()
            else:
                print("There are no groups to identify")
                self.pathLabel.config(text="Invalid")
                self.pathStatus.config(text="No groups to identify")

            self.pathLabel.config(text="Valid")
        else:
            print("Missing a folders")
            self.pathLabel.config(text="Invalid")

        if not self.pathReady:
            print("Not valid")
            self.pathLabel.config(text="Invalid")

    def checkForFiles(self):
        """Check if each group folder contains the necessary files."""
        for group in self.groupFolders:
            calibrationFileValidation = glob.glob(self.path + r"/{}/calibration/*.png".format(group))
            fishFileValidation = glob.glob(self.path + r"/{}/rs/rgb/*.png".format(group))
            outputPathValidation = os.path.isdir(self.path + r"/{}/output/")
            depthFileValidation = glob.glob(self.path + r"/{}/rs/depth/*.png".format(group))
            jsonFileValidation = glob.glob(self.path + r"/{}/rs/depth/*.json".format(group))

            # check if at least one png image exists in group_x/calibration/
            if len(calibrationFileValidation) == 0:
                print("Missing calibration files in {}".format(group))
                self.pathLabel.config(text="Invalid")
                self.pathStatus.config(text="Missing calibration files")
                break
            else:
                print("Calibration files are present in {}".format(group))

            # check if at least one png image exists in group_x/calibration/rs/rgb/
            if len(fishFileValidation) == 0:
                print("Missing fish files in {}".format(group))
                self.pathLabel.config(text="Invalid")
                self.pathStatus.config(text="Missing fish files")
                break
            else:
                print("Fish files are present in {}".format(group))

            # check if group_x/output/ folder exists
            if outputPathValidation is True:
                print("Missing output folder in {}".format(group))
                self.pathLabel.config(text="Invalid")
                self.pathStatus.config(text="Missing calibration files")
                break
            else:
                print("Output folder are present in {}".format(group))

            # check if at least one png image exists in group_x/calibration/rs/depth/
            if len(depthFileValidation) == 0:
                print("Missing depth files in {}".format(group))
                self.pathLabel.config(text="Invalid")
                self.pathStatus.config(text="Missing depth files")
                break
            else:
                print("Depth files are present in {}".format(group))

            # check if each found depth file has a corresponding json file
            for depthFile in depthFileValidation:
                jsonFile = depthFile[:-4] + ".json"
                if jsonFile not in jsonFileValidation:
                    print("Missing json file for {}".format(depthFile))
                    self.pathLabel.config(text="Invalid")
                    self.pathStatus.config(text="Missing json files")
                    break
                else:
                    print("Json file is present for {}".format(depthFile))
                    self.pathLabel.config(text="Valid")

        # if all groups are valid, then the program is ready to start
        if self.pathLabel.cget("text") == "Valid":
            print("All groups are valid")
            self.pathReady = True
            self.modifiedEntry = False
            return True
        else:
            print("Not all groups are valid")
            self.pathReady = False
            return False

    def start(self):
        """Goes to group selection page if path and connection are valid."""
        print("Entry modified? ", self.modifiedEntry)
        if self.pathReady and self.connectionReady and not self.modifiedEntry:
            # Check for tables named table_x in the mySQL database, and modify tableName to be one higher than the
            # highest table number. UNCOMMENT BELOW LATER
            while True:
                if (self.tableName,) in self.Database.pullall():
                    self.tableName = self.tableName[:-1] + str(int(self.tableName[-1]) + 1)
                    print("Table name already exists, changing to {}".format(self.tableName))
                else:
                    print("Table name is {}".format(self.tableName))
                    break

            # Create table in mySQL database
            print("Creating table")
            self.Database.createTable(self.tableName)
            print(self.Database.pullall())

            print("Group selection")
            self.controller.frames["PageOne"].insertGroups(self.groupFolders)
            self.controller.show_frame("PageOne")
        else:
            print("Not ready to start")


class PageOne(Frame):
    """Frame to show the group selection."""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="royalblue2")

        self.backButton = Button(self, text="Back", command=lambda: self.controller.show_frame("StartPage"),
                                 font=("Arial", "25"), bg="black", fg="white")
        self.backButton.place(relx=0.9, rely=0.9, anchor=CENTER)

        # Listbox to show all groups
        self.groupList = Listbox(self, selectmode="multiple", height=10, width=30, font=("Arial", "25"), bg="white",
                                 fg="black", justify='center')
        self.groupList.place(relx=0.5, rely=0.3, anchor=CENTER)

        # Two buttons underneath groupList to select and deselect all items.
        self.selectAllButton = Button(self, text="Select all", command=lambda: self.groupList.select_set(0, END),
                                      font=("Arial", "25"), bg="black", fg="white")
        self.selectAllButton.place(relx=0.4, rely=0.7, anchor=CENTER)
        self.deselectAllButton = Button(self, text="Deselect all", command=lambda: self.groupList.select_clear(0, END),
                                        font=("Arial", "25"), bg="black", fg="white")
        self.deselectAllButton.place(relx=0.6, rely=0.7, anchor=CENTER)

        # Button to start identification process
        self.startButton = Button(self, text="Start", command=lambda: self.start(),
                                  font=("Arial", "25"), bg="black", fg="white")
        self.startButton.place(relx=0.5, rely=0.9, anchor=CENTER)

    def insertGroups(self, groupFolders):
        self.groupList.delete(0, END)
        for group in groupFolders:
            self.groupList.insert(END, str(group))
            # self.groupList.itemconfig(str(group), bg="lime")

    def start(self):
        """Start identification process"""
        print("Starting identification")
        self.controller.show_frame("PageTwo")


class PageTwo(Frame):
    """Frame to show the identification progress"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="royalblue2")

        self.backButton = Button(self, text="Back", command=lambda: self.controller.show_frame("PageOne"),
                                 font=("Arial", "25"), bg="black", fg="white")
        self.backButton.place(relx=0.9, rely=0.9, anchor=CENTER)

        self.startButton = Button(self, text="Start", command=lambda: self.showProgress(),
                                  font=("Arial", "25"), bg="black", fg="white")
        self.startButton.place(relx=0.5, rely=0.9, anchor=CENTER)

        # Progressbar to show progress of identification
        self.progressBarAllGroups = Progressbar(self, orient=HORIZONTAL, length=500, mode='determinate')
        self.progressBarAllGroups.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.progressBarSeperateGroups = Progressbar(self, orient=HORIZONTAL, length=500, mode='determinate')
        self.progressBarSeperateGroups.place(relx=0.5, rely=0.7, anchor=CENTER)

        # Labels to indicate what the progressbars is showing
        self.progressBarAllGroupsLabel = ttkLabel(self, font=("Arial", "25"), text="Progress of all groups")
        self.progressBarAllGroupsLabel.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.progressBarSeperateGroupsLabel = ttkLabel(self, font=("Arial", "25"), text="Progress of individual group")
        self.progressBarSeperateGroupsLabel.place(relx=0.5, rely=0.6, anchor=CENTER)

    def update_progress_label(self, progressBar):
        return f"Current Progress: {progressBar['value']}%"

    def showProgress(self):
        self.tableName = self.controller.frames["StartPage"].tableName
        self.Database = self.controller.frames["StartPage"].Database
        self.groupSelection = self.controller.frames["PageOne"].groupList.curselection()
        self.groupFolders = [self.controller.frames["PageOne"].groupList.get(group) for group in self.groupSelection]
        print(self.groupFolders)
        # disable all buttons until identification is done
        self.startButton.config(state=DISABLED)
        self.backButton.config(state=DISABLED)

        # Use database.modifyTable() to add 10 rows with a random values in the columns Species, Lenght, Orientation, and GripPoints.
        # The Species column should be either "Cod" or "Haddock".
        # The Lenght column should be a random float between 30.0 and 100.0.
        # The Orientation column should be a random integer between 0 and 180.
        # The GripPoints column should be a random point, formatted as (x,y).
        import random
        print("Modifying table", self.tableName)
        for i in range(50):
            print("Fish {}".format(i+1))
            ID = i+1
            species = random.choice(['Hake', 'Cod', 'Haddock', 'Whiting', 'Saithe', 'Horse mackerel', '*others'])
            lenght = random.uniform(20.0, 60.0)
            orientation = (random.randint(0, 180), -random.randint(0, 180))
            gripPoints = (random.randint(0, 100), random.randint(0, 100))
            fishData = [ID, species, lenght, orientation[0], orientation[1], gripPoints[0], gripPoints[1]]
            self.Database.addFish(self.tableName, fishData)



        """import time
        self.progressBarAllGroups['value'] = 0
        for group in self.groupFolders:
            print(group)
            self.progressBarAllGroupsLabel.config(text="Progress of {}".format(group))
            # self.progressBarAllGroupsLabel['text'] = self.update_progress_label(self.progressBarAllGroups)
            self.progressBarAllGroups['value'] += 100 / len(self.groupFolders)
            self.progressBarSeperateGroups['value'] = 0
            for i in range(5):
                print(i)
                self.progressBarSeperateGroupsLabel.config(text="Doing task {}".format(i + 1))
                self.progressBarSeperateGroups['value'] += 20
                self.update_idletasks()
            self.update_idletasks()"""
        self.progressBarAllGroupsLabel.config(text="Done")

        # enable all buttons when identification is done
        self.startButton.config(state=NORMAL)
        self.backButton.config(state=NORMAL)


app = Main()
app.mainloop()
