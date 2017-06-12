from Tkinter import *
from ttk import *
import tkMessageBox
import Queue
from threading import Lock, Thread

from motor_details import Settings
from test_program.mocks.mock_axis import MockAxis
from test_program.comms.comms import create_connection
from test_program.motor_tests.dir_test import DirectionTest
from test_program.motor_tests.enc_test import EncoderTest
from test_program.motor_tests.rep_test import RepeatabilityTest
from test_program.motor_tests.bl_test import BacklashTest


class App(Frame):
    button_idx = 0
    in_queue = Queue.Queue()
    lock = Lock()

    def __init__(self, master=None):
        Frame.__init__(self, master, padding="5")

        self.grid(column=0, row=0, sticky=N+S+E+W)
        self.columnconfigure(0, weight=1)

        self.master.after(100, self.process_queue)

        try:
            self.g = create_connection(self._log)
        except Exception as e:
            # TODO: retry?
            tkMessageBox.showerror("Cannot connect", e.message)
            self.quit()

        #self.axis_a = Axis(self.g)
        self.axis = MockAxis(self.g)

        self.create_widgets()

        self.axis.setup()

    def process_queue(self):
        with self.lock:
            try:
                func = self.in_queue.get(0)
                func()
            except Queue.Empty:
                pass
            finally:
                self.master.after(100, self.process_queue)

    def _log(self, message):
        with self.lock:
            self.out_log.configure(state=NORMAL)
            self.out_log.insert(END, message + "\n")
            self.out_log.see(END)
            self.out_log.configure(state=DISABLED)

    def _create_test_button(self, name, test, requires_setup=True):
        test_button = Button(self, text=name)
        test_button.configure(command=lambda *args: self.run_test(test))
        if requires_setup:
            test_button.configure(state=DISABLED)
            self.axis.limits_found.trace("w", lambda *args: test_button.configure(state=NORMAL))
        self._place_button(test_button)

    def _place_button(self, button):
        button.grid(column=0, row=self.button_idx, sticky=N+S+E+W, pady="5")
        self.rowconfigure(self.button_idx, weight=1)
        self.button_idx += 1

    def quit(self):
        self.axis.stop()
        self.g.GClose()
        Frame.quit(self)

    def run_test(self, test):
        thread = Thread(target=test.perform_test)
        thread.daemon = True
        thread.start()

    def create_widgets(self):
        style = Style()
        style.configure("ST.TButton", foreground="red")

        dir_test = DirectionTest(self, self._log, self.axis)
        self._create_test_button("Setup", dir_test, False)

        enc_test = EncoderTest(self.axis, self._log, self.g)
        self._create_test_button("Test Encoder", enc_test)

        backlash_test = BacklashTest(self.axis, self._log, self.g)
        self._create_test_button("Backlash Test", backlash_test)

        self._place_button(Button(self, text="STOP MOTORS", style="ST.TButton", command=self.axis.stop))

        self._place_button(Button(self, text="Exit", command=self.quit))

        rhs = Panedwindow(self, orient=VERTICAL)
        rhs.grid(column=1, row=0, rowspan=self.button_idx, sticky=N+S+E+W, padx="5")
        rhs.rowconfigure(0, weight=2)
        rhs.rowconfigure(1, weight=1)

        mot_details = Settings(self.axis, backlash_test.repeats, rhs)
        mot_details.grid(column=0, row=0, sticky=N+S+E+W, pady="5")
        rhs.add(mot_details)

        self.out_log = Text(rhs, state=DISABLED)
        self.out_log.grid(column=0, row=1, sticky=N+S+E+W, pady="5")
        rhs.add(self.out_log)

"""
            print "Axis A setup"
            print "What tests would you like to perform?"
            print "2. Encoder/steps accuracy test"
            print "4. Analyse stats"
            print "5. Repeatability"
            print "6. Backlash"
            print "0. Exit"

            elif option == 4:
                stats = Statistics()
                stats.analyse_whole_folder("data")
            elif option == 5:
                rep = RepeatabilityTest(log)
                rep.perform_test(axis_a, 10000, 2)
            elif option == 6:
                bl = BacklashTest(log, g, 10)
                bl.perform_test(axis_a)
    finally:
        axis_a.stop()
"""