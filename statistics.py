import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os

class Statistics():
    def __init__(self):
        pass

    def plot_gauss_fit(self, errors, label):

        errors = np.sort(errors)

        fit = stats.norm.pdf(errors, np.mean(errors), np.std(errors))

        plt.plot(errors, fit, label=label)

    def remove_harmonic(self, errors, freq):
        fft = np.fft.rfft(errors)
        freqs = np.fft.rfftfreq(errors.shape[-1])
        idx = np.abs(freqs-freq).argmin()
        fft[idx-5:idx+5] = 0
        return np.fft.irfft(fft)

    def plot_fft(self, errors, label):
        fft = np.fft.rfft(errors)
        freq = np.fft.rfftfreq(errors.shape[-1])

        plt.plot(freq, fft, label=label)

    def analyse_data_from_file(self, filename):
        data = np.loadtxt(filename, delimiter=",")
        errors = self.get_errors(data)
        #self.add_to_plot(np.array([data[0], errors]))

        print "Errors between {} and {}".format(np.min(errors), np.max(errors))

        velo = filename.split("_")[-1]


        plt.plot(data[0], errors, label=velo)


    def get_errors(self, data):
        microstepping = 16
        motor_res = 0.001

        b, c = np.polyfit(data[0], data[1], 1)

        print "B: {},  C: {}".format(b, c)

        # Calculate the error from the theoretical value and convert to microns
        vfunc = np.vectorize(lambda x, y: ((b*x+c)-y)*1000*motor_res/microstepping)

        return vfunc(data[0], data[1])

    def analyse_whole_folder(self, folder):
        files = os.listdir(folder)
        for f in files:
            if "_1000_" in f:
                print "\nFor: " + str(f)
                filename = os.path.join(folder, f)

                self.analyse_data_from_file(filename)

        plt.legend()
        plt.show()