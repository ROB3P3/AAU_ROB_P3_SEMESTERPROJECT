import glob
import tkinter as tk
from tkinter import *
from tkinter import filedialog
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
            self.title("Main Menu")
            self.geometry("1000x800")
        elif page_name == "PageOne":
            self.title("Select groups to identify")
            self.geometry("1000x800")
        elif page_name == "PageTwo":
            self.title("Showing Progess...")
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

        # check if entry fields have been modified since last check
        # to prevents user from validating one oath and then changing the path without validating again.
        self.modifiedEntry = False

        self.titleText = Label(self, font=("Arial", "40"), text="Welcome to the fish zone", bg="royalblue2",
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
            Database = DatabaseHandler.Database(IPAdress, port)
            isConnected = Database.connect()
            self.connectionLabel.config(text="Connected")
            self.connectionReady = True
            print("Connection is: ", isConnected)
            print(Database.pullall())
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
        """Start identification process"""
        print("Entry modified? ", self.modifiedEntry)
        if self.pathReady and self.connectionReady and not self.modifiedEntry:
            print("Starting identification")
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

        self.groupList = Listbox(self, selectmode="multiple", height=10, width=30, font=("Arial", "25"), bg="white",
                                 fg="black", justify='center')
        self.groupList.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Two buttons underneath groupList to select and deselect all items.
        self.selectAllButton = Button(self, text="Select all", command=lambda: self.groupList.select_set(0, END),
                                      font=("Arial", "25"), bg="black", fg="white")
        self.selectAllButton.place(relx=0.3, rely=0.9, anchor=CENTER)
        self.deselectAllButton = Button(self, text="Deselect all", command=lambda: self.groupList.select_clear(0, END),
                                        font=("Arial", "25"), bg="black", fg="white")
        self.deselectAllButton.place(relx=0.7, rely=0.9, anchor=CENTER)

        # Button to start identification process
        self.startButton = Button(self, text="Start", command=lambda: self.start(),
                                  font=("Arial", "25"), bg="black", fg="white")
        self.startButton.place(relx=0.5, rely=0.9, anchor=CENTER)

    def insertGroups(self, groupFolders):
        for group in groupFolders:
            self.groupList.insert(END, str(group))
            #self.groupList.itemconfig(str(group), bg="lime")

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

        self.BackButton = Button(self, text="Back", command=lambda: self.controller.show_frame("StartPage"),
                                 font=("Arial", "25"), bg="black", fg="white")
        self.BackButton.place(relx=0.9, rely=0.9, anchor=CENTER)


app = Main()
app.mainloop()
