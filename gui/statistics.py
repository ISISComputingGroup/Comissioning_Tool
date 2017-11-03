import numpy as np
from random import random
from scipy import interpolate
import os

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

from tkinter import ttk, BooleanVar, Toplevel, filedialog, TOP, BOTTOM, BOTH, LEFT, Y


class Statistics(ttk.Frame):
    data = dict()

    def __init__(self, master, axis):
        ttk.Frame.__init__(self, master, padding="5")

        self.axis = axis

        self.is_gaussian = BooleanVar(value=False)
        self.is_gaussian.trace("w", self.replot)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.fig.add_subplot(111)

        self._create_widgets()

    def replot(self, *args):
        self.plot.clear()
        if self.is_gaussian.get():
            for name, errors in self.data.iter():
                self.plot_probability(name, errors[1])

            self.plot.set_xlabel("Error (microns)")
            self.plot.set_ylabel("Probability")
        else:
            for name, errors in self.data.iter():
                self.plot.plot(errors[0], errors[1], label=name)

            self.plot.set_xlabel("Encoder Value")
            self.plot.set_ylabel("Error (microns)")

        self.plot.legend()
        self.fig.canvas.draw()

    def plot_probability(self, label, errors):
        hist, bins = np.histogram(errors, bins=50, density=True)
        centers = (bins[:-1] + bins[1:]) / 2

        prob = interpolate.InterpolatedUnivariateSpline(centers, hist)

        color = (random(), random(), random())
        xp = np.linspace(centers[0], centers[-1], 100)
        self.plot.plot(centers, hist, '.', color=color)
        self.plot.plot(xp, prob(xp), '-', color=color, label=label)

    def analyse_data(self, name, data):
        i = 0
        temp_name = name
        while temp_name in self.data.keys():
            i += 1
            temp_name = name + "_{}".format(i)
        name = temp_name

        errors = self.get_errors(data)

        self.data[name] = np.array([data[0], errors])

    def analyse_data_from_file(self, filename):
        data = np.loadtxt(filename, delimiter=",")
        filename = os.path.split(filename)[1].split(".")[0]
        self.analyse_data(filename, data)

    def more_details(self):
        window = Toplevel(self)
        u = " ("+chr(181)+"m)"
        columns = ("Min Error" + u, "Max Error" + u, "Mean Error" + u, "Standard Deviation" + u)

        data_grid = ttk.Treeview(window, columns=columns)

        i = 0
        data_grid.heading('#{}'.format(i), text="File")

        for c in columns:
            i += 1
            data_grid.heading('#{}'.format(i), text=c)

        for name, errors in self.data.iteritems():
            err = errors[1]
            data_grid.insert('', 0, iid=name, text=name)
            i = 0
            for v in [np.min(err), np.max(err), np.mean(err), np.std(err)]:
                data_grid.set(name, column=i, value="{:.3g}".format(v))
                i += 1

        data_grid.pack()

    def get_errors(self, data):
        b, c = np.polyfit(data[0], data[1], 1)

        b = self.axis.microstep.get()/(self.axis.motor_res.get()*self.axis.enc_res.get())

        # Calculate the error from the theoretical value and convert to microns
        vfunc = np.vectorize(lambda x, y: ((b*x+c)-y)*self.axis.motor_res.get()/self.axis.microstep.get())

        return vfunc(data[0], data[1])

    def change_axis(self, axis):
        self.axis = axis

    def _load_data(self):
        files = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Text", "*.txt")], multiple=1)
        for f in files:
            self.analyse_data_from_file(f)
        self.replot()

    def _clear(self):
        self.data = dict()
        self.plot.clear()
        self.fig.canvas.draw()

    def _create_widgets(self):
        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        toolbar.pack(side=BOTTOM)

        ttk.Separator(toolbar).pack(side=LEFT, fill=Y, padx="10")
        ttk.Button(toolbar, text="Load", command=self._load_data).pack(side=LEFT, fill=Y)
        ttk.Button(toolbar, text="Clear", command=self._clear).pack(side=LEFT, fill=Y)
        ttk.Button(toolbar, text="More Details", command=self.more_details).pack(side=LEFT, fill=Y)
        ttk.Checkbutton(toolbar, text="Prob. Dist.", variable=self.is_gaussian).pack(side=LEFT, fill=Y)

        canvas._tkcanvas.pack(side=TOP)
