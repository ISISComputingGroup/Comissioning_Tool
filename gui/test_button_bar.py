from Tkinter import *
import ttk
import tkMessageBox
from threading import Thread
from test_program.motor_tests.dir_test import DirectionTest
from test_program.motor_tests.enc_test import EncoderTest
from test_program.motor_tests.rep_test import RepeatabilityTest
from test_program.motor_tests.bl_test import BacklashTest


class TestButtonBar(Frame):
    button_idx = 0
    test_buttons = []

    def __init__(self, axis, settings_panel, parent):
        Frame.__init__(self, parent)
        self.axis = axis
        self.parent = parent
        self.events = parent.events
        self.log = parent.log
        self.g = parent.g
        self.test_settings = settings_panel

        self.create_widgets()

    def enable_buttons(self):
        if self.axis.limits_found.get():
            for t in self.test_buttons:
                t.configure(state=NORMAL)
        else:
            self.test_buttons[0].configure(state=NORMAL)

    def _create_test_button(self, test, starting_state=DISABLED):
        test_button = ttk.Button(self, text=test.name, state=starting_state)
        test_button.configure(command=lambda: self.run_test(test))

        self._place_button(test_button)
        self.test_buttons.append(test_button)

        if getattr(test, "get_settings_ui", False):
            group = ttk.LabelFrame(self.test_settings, text=test.name, padding=5)
            test.get_settings_ui(group)
            group.pack(fill=X, pady=5, padx=5)

    def _place_button(self, button):
        button.pack(fill=BOTH, expand=1, pady="5")
        self.rowconfigure(self.button_idx, weight=1)

    def manual_stop(self):
        self.axis.stop()
        self.axis.safe_to_move = False
        self.enable_buttons()

    def run_test(self, test):
        if not self.axis.safe_to_move:
            msg = "The last motion was manually stopped. Is it now safe to proceed?"
            if tkMessageBox.askyesno("Motor State", msg):
                self.axis.safe_to_move = True
            else:
                return

        thread = Thread(target=test.run)
        thread.daemon = True
        thread.start()
        for t in self.test_buttons:
            t.configure(state=DISABLED)
        test.running.trace("w", lambda *args: self.events.put(self.enable_buttons))

    def toggle_connection(self):
        if self.parent.connection_open:
            for t in self.test_buttons:
                t.configure(state=DISABLED)
            self.stop_button.configure(state=DISABLED)
            new_text = "Reconnect"
        else:
            self.stop_button.configure(state=NORMAL)
            self.test_buttons[0].configure(state=NORMAL)
            new_text = "Disconnect"

        self.disconnect_button.configure(text=new_text)
        self.parent.toggle_connection()

    def create_widgets(self):
        dir_test = DirectionTest(self.events, self.parent.log, self.axis)
        self._create_test_button(dir_test, NORMAL)

        enc_test = EncoderTest(self.events, self.log, self.axis, self.g)
        self._create_test_button(enc_test)

        backlash_test = BacklashTest(self.events, self.log, self.axis, self.g)
        self._create_test_button(backlash_test)

        repeat_test = RepeatabilityTest(self.events, self.log, self.axis)
        self._create_test_button(repeat_test)

        self.axis.limits_found.trace("w", lambda *args: self.events.put(self.enable_buttons))

        self.stop_button = Button(self, text="STOP MOTORS", command=self.manual_stop, bg='#FF0000')
        self._place_button(self.stop_button)

        self.disconnect_button = ttk.Button(self, text="Disconnect", command=self.toggle_connection)
        self._place_button(self.disconnect_button)

        self._place_button(ttk.Button(self, text="Exit", command=self.parent.quit))