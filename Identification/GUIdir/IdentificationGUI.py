import glob
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter.ttk import Label as ttkLabel
#from Identification.DATAdir import DatabaseHandler as DatabaseHandler
import DATAdir.DatabaseHandler as DatabaseHandler
import os
import LOGIKdir.Logik as Logik
from multiprocessing import freeze_support


class Main(Tk):
    def __init__(self):
        freeze_support()
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

        self.pathValid = False
        self.path = None
        self.groupFolders = []
        self.groupAmount = len(self.groupFolders)
        self.pathReady = False

        # check if entry fields have been modified since last check
        # to prevents user from validating one oath and then changing the path without validating again.
        self.modifiedEntry = False

        self.titleText = Label(self, font=("Arial", "40"), text="Fish Identification", bg="royalblue2", fg="black")
        self.titleText.place(relx=0.5, rely=0.10, anchor=CENTER)
        self.startButton = Button(self, text="Select Groups", command=lambda: self.start(), font=("Arial", "25"), bg="black", fg="white")
        self.startButton.place(relx=0.5, rely=0.75, anchor=CENTER)
        # Disable startButton until path is valid
        self.startButton.config(state=DISABLED)

        self.quitButton = Button(self, text="Exit", command=exit, font=("Arial", "20"), bg="black", fg="white")
        self.quitButton.place(relx=0.5, rely=0.90, anchor=CENTER)

        # Label underneath pathButton to indicate isConnected, change when pathButton is pressed.
        self.pathLabel = Label(self, font=("Arial", "15"), text="Not valid", bg="royalblue2", fg="black")
        self.pathLabel.place(relx=0.85, rely=0.46, anchor=CENTER)

        # label underneath pathField to indicate status of path
        self.pathStatus = Label(self, font=("Arial", "15"), text="Enter path", bg="royalblue2", fg="black")
        self.pathStatus.place(relx=0.5, rely=0.46, anchor=CENTER)


        # Path address and check
        self.pathValue = StringVar()
        self.pathValue.trace('w', self.checkPathInput)
        self.pathField = Entry(self, font=("Arial", "25"), width=30, bg="white", fg="black",
                               textvariable=self.pathValue)
        self.pathField.place(relx=0.5, rely=0.40, anchor=CENTER)
        # insert test path
        self.pathField.insert(tk.END, r"C:/FishProject")
        self.pathButton = Button(self, text="Check", command=lambda: self.checkPath(), font=("Arial", "20"), bg="black",
                                 fg="white")
        self.pathButton.place(relx=0.85, rely=0.4, anchor=CENTER)

        # Labels to indicate function of widget
        self.pathlabel = Button(self, font=("Arial", "25"), text="Path to root:", bg="royalblue2", fg="black",
                                command=lambda: self.askForPath())
        self.pathlabel.place(relx=0.11, rely=0.4, anchor=CENTER)

    def checkPathInput(self, *args):
        """Reacts if pathField has been modified."""
        self.modifiedEntry = True
        self.pathLabel.config(text="Invalid")
        self.pathStatus.config(text="Path modified")
        # Disable startButton until path is valid
        self.startButton.config(state=DISABLED)
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
            calibrationFileValidation = glob.glob(self.path + r"/{}/calibration/rs/*.png".format(group))
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
            # Enable startButton
            self.startButton.config(state=NORMAL)
            return True
        else:
            print("Not all groups are valid")
            self.pathReady = False
            return False

    def start(self):
        """Goes to group selection page if path and connection are valid."""
        print("Entry modified? ", self.modifiedEntry)
        if self.pathReady and not self.modifiedEntry:
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
        self.parent = parent

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
        self.startButton = Button(self, text="Start", command=lambda: self.startIdentification(),
                                  font=("Arial", "25"), bg="black", fg="white")
        self.startButton.place(relx=0.5, rely=0.9, anchor=CENTER)

    def insertGroups(self, groupFolders):
        self.groupList.delete(0, END)
        for group in groupFolders:
            self.groupList.insert(END, str(group))
            # self.groupList.itemconfig(str(group), bg="lime")

    def startIdentification(self): ###################################################################################### Starts the ID process
        """Start identification process"""
        print("Starting identification")
        self.selectedGroups = []
        for  i in self.groupList.curselection():
            self.selectedGroups.append(int(self.groupList.get(i).split("_")[1]))
        #list = (self.groupList.get(group) for group in self.groupList.curselection())
        print(self.selectedGroups)
        #print((self.groupList.curselection()).split("_"))
        print(self.controller.frames["StartPage"].path)
        
        #self.controller.show_frame("PageTwo") # here the update progress page is called to display

        # starts the Identification process for the selected groups
        Logik.logicStart(self.controller.frames["StartPage"].path, self.selectedGroups)



class PageTwo(Frame):
    """Frame to show the identification progress. This is not currently in use and can be ignored"""

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
        print(self.groupFolders, "WTF")
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



        self.progressBarAllGroups['value'] = 0
        for group in self.groupFolders:
            print(group)
            self.progressBarAllGroupsLabel.config(text="Progress of {}".format(group))
            # self.progressBarAllGroupsLabel['text'] = self.update_progress_label(self.progressBarAllGroups)
            self.progressBarAllGroups['value'] += 100 / (len(self.groupFolders)+1)
            self.progressBarSeperateGroups['value'] = 0
            #while len(glob.glob("C:/P3OutData/Merged/group_{}/Edge/*.png".format(group))) < len(glob.glob("{}/{}/rs/rgb/*.png".format(self.controller.frames["StartPage"].path,group))):
            self.progressBarSeperateGroupsLabel.config(text="Doing task {}".format(i + 1)) #
            self.progressBarSeperateGroups['value'] = (len(glob.glob("C:/P3OutData/Merged/{}/Edge/*.png".format(group))) / len(glob.glob("{}/{}/rs/rgb/*.png".format(self.controller.frames["StartPage"].path,group))))* 100
            self.update_idletasks()
            print("Hello from task update")
            self.update_idletasks()
        self.progressBarAllGroupsLabel.config(text="Done")

        # enable all buttons when identification is done
        self.startButton.config(state=NORMAL)
        self.backButton.config(state=NORMAL)


