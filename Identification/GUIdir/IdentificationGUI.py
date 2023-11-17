import tkinter
from tkinter import *
import Identification.LOGIKdir as Logik
import Identification.DATAdir as Data

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
        for page in (StartPage, PageOne):
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
        self.titleText = Label(self, font=("Arial", "40"), text="Welcome to the fish zone", bg="royalblue2",
                               fg="black").place(relx=0.5, rely=0.10, anchor=CENTER)
        self.startButton = Button(self, text="Start", command=lambda: self.controller.show_frame("PageOne"),
                                  font=("Arial", "25"), bg="black", fg="white").place(relx=0.5, rely=0.75,
                                                                                      anchor=CENTER)
        self.quitButton = Button(self, text="Exit", command=exit, font=("Arial", "20"), bg="black", fg="white").place(
            relx=0.5, rely=0.90, anchor=CENTER)

        # IP address, port, and check
        # self.IPField = Text(self, font=("Arial", "25"), height=1, width=12, bg="white", fg="black")
        self.IPField = Entry(self, font=("Arial", "25"), width=12, bg="white", fg="black")
        self.IPField.place(relx=0.3, rely=0.20, anchor=CENTER)
        self.IPField.insert(tkinter.END, "172.26.51.10")
        # self.portField = Text(self, font=("Arial", "25"), height=1, width=5, bg="white", fg="black")
        self.portField = Entry(self, font=("Arial", "25"), width=4, bg="white", fg="black")
        self.portField.place(relx=0.55, rely=0.20, anchor=CENTER)
        self.portField.insert(tkinter.END, "3306")
        self.connectButton = Button(self, text="Connect", command=lambda: self.checkConnection(), font=("Arial", "20"),
                                    bg="black", fg="white").place(relx=0.75, rely=0.2, anchor=CENTER)

        # Labels to indicate function of widget
        self.IPlabel = Label(self, font=("Arial", "25"), text="IP:", bg="royalblue2",
                             fg="black").place(relx=0.15, rely=0.20, anchor=CENTER)
        self.portlabel = Label(self, font=("Arial", "25"), text="Port:", bg="royalblue2",
                               fg="black").place(relx=0.46, rely=0.20, anchor=CENTER)

    def checkConnection(self):
        IPAdress = str(self.IPField.get())
        IPAdressList = IPAdress.rsplit(".", -1)
        port = str(self.portField.get())
        print("IP: {} Port: {}".format(IPAdress, port))
        if len(IPAdressList) == 4:
            valueValidation = all(int(number) <= 255 for number in IPAdressList)
            lenghtValidation = all(len(number) <= 3 for number in IPAdressList)
            if valueValidation is True and lenghtValidation is True:
                print("Valid IP")
                if len(port) == 4 and port.isdigit() is True:
                    print("Valid Port, attempting connection.")
                    Data.DatabaseHandler.Database(IPAdress)
                else:
                    print("Invalid port: ", port)
            elif valueValidation is False and lenghtValidation is True:
                print("Invalid IP: a number is too big")
            elif valueValidation is True and lenghtValidation is False:
                print("Invalid IP: a number is too long")
            else:
                print("Invalid IP: a number is too big and long")
        else:
            print("Invalid IP: not enough separations \n", IPAdress.rsplit(".", -1))

    def checkPath(self):
        pass


class PageOne(Frame):
    """Frame to show the identification progress"""

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg="royalblue2")
        self.BackButton = Button(self, text="Back", command=lambda: self.controller.show_frame("StartPage"),
                                 font=("Arial", "25"), bg="black", fg="white").place(relx=0.5, rely=0.45, anchor=CENTER)


app = Main()
app.mainloop()
