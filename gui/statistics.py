import numpy as np
import scipy.stats as stats
import os

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from Tkinter import *
from ttk import *


class Statistics(Frame):
    data = dict()

    def __init__(self, master):
        Frame.__init__(self, master, padding="5")

        self.microstepping = IntVar(value=16)
        self.motor_res = DoubleVar(value=0.001)

        self._create_widgets()

    def plot_gauss_fit(self, errors, label):
        errors = np.sort(errors)

        fit = stats.norm.pdf(errors, np.mean(errors), np.std(errors))

        self.plot.plot(errors, fit, label=label)

    def analyse_data(self, name, data):
        i = 0
        temp_name = name
        while temp_name in self.data.keys():
            i += 1
            temp_name = name + "_{}".format(i)
        name = temp_name

        errors = self.get_errors(data)

        self.data[name] = errors

        self.plot.plot(data[0], errors, label=name)

    def analyse_data_from_file(self, filename):
        data = np.loadtxt(filename, delimiter=",")
        self.analyse_data(filename, data)

    def more_details(self):
        window = Toplevel(self)
        data_grid = Treeview(window, columns=("Max Error", "Mean Error", "Standard Deviation"))

        data_grid.heading('#0', text="File")
        data_grid.heading('#1', text="Max Error")
        data_grid.heading('#2', text="Mean Error")
        data_grid.heading('#3', text="Standard Deviation")

        for name, err in self.data.iteritems():
            data_grid.insert('', 0, iid=name, text=name)
            data_grid.set(name, column=0, value=max(np.max(err), np.min(err), key=abs))
            data_grid.set(name, column=1, value=np.mean(err))
            data_grid.set(name, column=2, value=np.std(err))

        data_grid.pack()


    def get_errors(self, data):
        b, c = np.polyfit(data[0], data[1], 1)

        # Calculate the error from the theoretical value and convert to microns
        vfunc = np.vectorize(lambda x, y: ((b*x+c)-y)*1000*self.motor_res.get()/self.microstepping.get())

        return vfunc(data[0], data[1])

    def analyse_whole_folder(self, folder):
        files = os.listdir(folder)
        for f in files:
            if "forward" in f and "test" not in f:
                filename = os.path.join(folder, f)

                self.analyse_data_from_file(filename)

    def _create_widgets(self):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.fig.add_subplot(111)

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        toolbar.pack(side=BOTTOM)

        Separator(toolbar).pack(side=LEFT, fill=Y, padx="20")
        Button(toolbar, text="Save Data").pack(side=LEFT, fill=Y)
        Button(toolbar, text="Load Data").pack(side=LEFT, fill=Y)
        Button(toolbar, text="More Details", command=self.more_details).pack(side=LEFT, fill=Y, padx="10")
        Checkbutton(toolbar, text="Gaussian").pack(side=LEFT, fill=Y)

        canvas._tkcanvas.pack(side=TOP)

        self.analyse_whole_folder("data")

        self.plot.legend()
