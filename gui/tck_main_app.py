from Tkinter import *
from ttk import *
import tkMessageBox
import Queue
import sys
from threading import Lock, Thread

from motor_details import Settings
from statistics import Statistics
from test_program.mocks.mock_axis import MockAxis
from test_program.axis import Axis
from test_program.comms.comms import create_connection
from test_program.motor_tests.dir_test import DirectionTest
from test_program.motor_tests.enc_test import EncoderTest
from test_program.motor_tests.rep_test import RepeatabilityTest
from test_program.motor_tests.bl_test import BacklashTest


class App(Frame):
    button_idx = 0
    in_queue = Queue.Queue()
    lock = Lock()
    test_buttons = []
    connection_open = True

    def __init__(self, master=None):
        Frame.__init__(self, master, padding="5")

        self.master = master

        self.grid(column=0, row=0, sticky=N+S+E+W)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self.master.after(100, self.process_queue)

        try:
            self.g = create_connection(self.log)
        except Exception as e:
            # TODO: retry?
            tkMessageBox.showerror("Cannot connect", e.message)
            self.quit()

        #self.axis = Axis(self.g)
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

    def log(self, message):
        with self.lock:
            self.out_log.configure(state=NORMAL)
            self.out_log.insert(END, message + "\n")
            self.out_log.see(END)
            self.out_log.configure(state=DISABLED)

    def _create_test_button(self, test, requires_setup=True):
        test_button = Button(self, text=test.name)
        test_button.configure(command=lambda: self.run_test(test))
        if requires_setup:
            test_button.configure(state=DISABLED)
            self.axis.limits_found.trace("w", lambda *args: test_button.configure(state=NORMAL))
        self._place_button(test_button)
        self.test_buttons.append(test_button)

        settings = Frame(self.notebook, padding="20")
        test.get_settings_ui(settings)
        if len(settings.winfo_children()) > 0:
            self.notebook.add(settings, text="{} Settings".format(test.name))

    def _place_button(self, button):
        button.grid(column=0, row=self.button_idx, sticky=N+S+E+W, pady="5")
        self.rowconfigure(self.button_idx, weight=1)
        self.button_idx += 1

    def quit(self):
        self.axis.stop()
        self.g.GClose()
        self.master.destroy()

    def run_test(self, test):
        thread = Thread(target=test.run)
        thread.daemon = True
        thread.start()
        for t in self.test_buttons:
            t.configure(state=DISABLED)
        test.running.trace("w", lambda *args: self.in_queue.put(self.test_finished))

    def test_finished(self):
        for t in self.test_buttons:
            t.configure(state=NORMAL)

    def toggle_connection(self):
        if self.connection_open:
            self.g.GClose()
            new_state = DISABLED
            new_text = "Reconnect"
        else:
            self.g = create_connection(self.log)
            new_state = NORMAL
            new_text = "Disconnect"

        self.connection_open = not self.connection_open

        for t in self.test_buttons:
            t.configure(state=new_state)

        self.stop_button.configure(state=new_state)

        self.disconnect_button.configure(text=new_text)


    def create_widgets(self):
        rhs = Panedwindow(self, orient=VERTICAL)

        self.notebook = Notebook(rhs)

        mot_details = Settings(self.axis, self.notebook)
        self.notebook.add(mot_details, text="Motor Settings")
        rhs.add(self.notebook)

        self.out_log = Text(rhs, state=DISABLED)
        rhs.add(self.out_log)

        style = Style()
        style.configure("ST.TButton", foreground="red")

        dir_test = DirectionTest(self.in_queue, self.log, self.axis)
        self._create_test_button(dir_test, False)

        enc_test = EncoderTest(self.in_queue, self.log, self.axis, self.g)
        self._create_test_button(enc_test)

        backlash_test = BacklashTest(self.in_queue, self.log, self.axis, self.g)
        self._create_test_button(backlash_test)

        repeat_test = RepeatabilityTest(self.in_queue, self.log, self.axis)
        self._create_test_button(repeat_test)

        self.stop_button = Button(self, text="STOP MOTORS", style="ST.TButton", command=self.axis.stop)
        self._place_button(self.stop_button)

        self.disconnect_button = Button(self, text="DISCONNECT", command=self.toggle_connection)
        self._place_button(self.disconnect_button)

        self._place_button(Button(self, text="Exit", command=self.quit))

        rhs.grid(column=1, row=0, rowspan=self.button_idx, sticky=N+S+E+W, padx="5")
        rhs.rowconfigure(0, weight=2)
        rhs.rowconfigure(1, weight=1)

        self.notebook.add(Statistics(self), text="Analysis")