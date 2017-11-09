from tkinter import ttk, messagebox, filedialog, N, S, E, W, HORIZONTAL, VERTICAL, BOTH, DISABLED, NORMAL, END, Text
import os
from datetime import date

from gui.test_button_bar import TestButtonBar
from gui.event_handler import EventHandler
from gui.motor_details import MotorSettings
from gui.statistics import Statistics
from mocks.mock_axis import MockAxis
from axis import LoggingAxis
from comms.comms import create_connection


class App(ttk.Frame):
    """
    The main window for the app.
    """
    axes = dict()

    def __init__(self, mock_connection=False, master=None):
        ttk.Frame.__init__(self, master, padding="5")
        self.mock = mock_connection
        self.master = master

        self.grid(column=0, row=0, sticky=N+S+E+W)

        self.events = EventHandler(master)

        try:
            self.g = create_connection(mock_connection, self.log)
        except IOError as e:
            # TODO: retry?
            msg = "Cannot connect to Galil."
            msg += "\nEnsure that: "
            msg += "\n   No other programs are communicating with the Galil."
            msg += "\n   The Galil is communicating at 115200 baud."

            messagebox.showerror("Cannot Connect", msg)
            self.quit()

        self.current_axis = self._create_axis("A", mock_connection)

        self.create_widgets()

        self.axes[self.current_axis.axis_letter] = self.current_axis

        self.current_axis.setup()

    def _create_axis(self, letter, mock=False, old_axis=None):
        if mock:
            return MockAxis(self.g, letter, old_axis)
        else:
            return LoggingAxis(self.g, letter, old_axis)

    def _log(self, message):
        self.out_log.configure(state=NORMAL)
        self.out_log.insert(END, message + "\n")
        self.out_log.see(END)
        self.out_log.configure(state=DISABLED)

    def log(self, message):
        self.events.put(lambda: self._log(message))

    def quit(self):
        self.current_axis.stop()
        self.g.GClose()
        self.master.destroy()

    def change_axis(self, new_axis):
        self.log("Changing to axis {}".format(new_axis))
        self.current_axis.stop()
        if new_axis in self.axes:
            self.current_axis = self.axes[new_axis]
        else:
            self.current_axis = self._create_axis(new_axis, self.mock, self.current_axis)
            self.axes[new_axis] = self.current_axis
        self.current_axis.setup()
        self.mot_details.bind_axis(self.current_axis)
        self.buttons.change_axis(self.current_axis)
        self.stats.change_axis(self.current_axis)

    def save_all(self):
        try:
            filename = filedialog.asksaveasfilename(initialdir=os.getcwd(), filetypes=[("Text", "*.txt")])

            if filename != '':
                out = "Test performed on {}\n".format(date.today().strftime("%d/%m/%y"))
                [out.__add__("\n{}\n".format(axis)) for axis in self.axes.values()]

                with open(filename, mode="w") as f:
                    f.write(out)

                self.log("File saved")
        except Exception as e:
            self.log("File failed to save: {}".format(e.message))

    def create_widgets(self):
        overall = ttk.Panedwindow(self, orient=HORIZONTAL)
        overall.pack(fill=BOTH, expand=1)

        rhs = ttk.Panedwindow(self, orient=VERTICAL)

        notebook = ttk.Notebook(rhs)

        self.mot_details = MotorSettings(self.current_axis, notebook, self.change_axis)
        self.mot_details.pack(fill=BOTH, expand=1)
        notebook.add(self.mot_details, text="Motor Settings")

        test_settings = ttk.Frame(notebook)
        notebook.add(test_settings, text="Test Settings")
        rhs.add(notebook)

        self.out_log = Text(rhs, state=DISABLED)
        rhs.add(self.out_log)

        self.buttons = TestButtonBar(self.current_axis, test_settings, self)

        overall.add(self.buttons, weight=1)
        overall.add(rhs, weight=2)

        self.stats = Statistics(self, self.current_axis)
        notebook.add(self.stats, text="Analysis")
