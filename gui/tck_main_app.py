from Tkinter import *
import ttk
import tkMessageBox
from threading import Thread

from test_button_bar import TestButtonBar
from event_handler import EventHandler
from motor_details import MotorSettings
from statistics import Statistics
from test_program.mocks.mock_axis import MockAxis
from test_program.axis import LoggingAxis
from test_program.comms.comms import create_connection, open_connection


class App(ttk.Frame):
    connection_open = True

    def __init__(self, master=None):
        ttk.Frame.__init__(self, master, padding="5")

        self.master = master

        self.grid(column=0, row=0, sticky=N+S+E+W)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.events = EventHandler(master)

        try:
            self.g = create_connection(self.log)
        except Exception as e:
            # TODO: retry?
            tkMessageBox.showerror("Cannot connect", e.message)
            self.quit()

        self.axis = LoggingAxis(self.g)
        #self.axis = MockAxis(self.g)

        self.create_widgets()

        self.axis.setup()

    def _log(self, message):
        self.out_log.configure(state=NORMAL)
        self.out_log.insert(END, message + "\n")
        self.out_log.see(END)
        self.out_log.configure(state=DISABLED)

    def log(self, message):
        self.events.put(lambda: self._log(message))

    def quit(self):
        self.axis.stop()
        self.g.GClose()
        self.master.destroy()

    def toggle_connection(self):
        if self.connection_open:
            self.log("Closing connection")
            self.g.GClose()
        else:
            self.log("Opening new connection")
            open_connection(self.g)

        self.connection_open = not self.connection_open

    def create_widgets(self):
        rhs = ttk.Panedwindow(self, orient=VERTICAL)

        notebook = ttk.Notebook(rhs)

        mot_details = MotorSettings(self.axis, notebook)
        notebook.add(mot_details, text="Motor Settings")

        test_settings = Frame(notebook)
        notebook.add(test_settings, text="Test Settings")
        rhs.add(notebook)

        self.out_log = Text(rhs, state=DISABLED)
        rhs.add(self.out_log)

        lhs = TestButtonBar(self.axis, test_settings, self)

        lhs.grid(column=0, row=0, sticky=N+S+E+W, padx="5")

        rhs.grid(column=1, row=0, sticky=N+S+E+W, padx="5")

        notebook.add(Statistics(self), text="Analysis")