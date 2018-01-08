from tkinter import ttk, messagebox, NORMAL, DISABLED, X, BOTH, Button
from comms.comms import stop_all, open_connection
from threading import Thread
from motor_tests.dir_test import DirectionTest
from motor_tests.encoder_test import EncoderTest
from motor_tests.rep_test import RepeatabilityTest
from motor_tests.back_lash_test import BacklashTest


class TestButtonBar(ttk.Frame):
    button_idx = 0
    test_buttons = []
    connection_open = True

    def __init__(self, axis, settings_panel, parent):
        ttk.Frame.__init__(self, parent)
        self.axis = axis
        self.parent = parent
        self.events = parent.events
        self.log = parent.log
        self.g = parent.g
        self.test_settings = settings_panel

        self.create_widgets()

    def change_axis(self, new_axis):
        self.axis = new_axis
        self.enable_buttons()

    def enable_buttons(self):
        if self.axis.limits_found.get():
            [t.configure(state=NORMAL) for t in self.test_buttons]
        else:
            [t.configure(state=DISABLED) for t in self.test_buttons]

            self.test_buttons[0].configure(state=NORMAL)

    def _create_test_button(self, test_type, starting_state=DISABLED):
        test = test_type(self.events, self.log, self.axis, self.g)
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
        stop_all(self.g)
        self.axis.safe_to_move = False
        self.enable_buttons()

    def run_test(self, test):
        if not self.axis.safe_to_move:
            msg = "The last motion was manually stopped. Is it now safe to proceed?"
            if messagebox.askyesno("Motor State", msg):
                self.axis.safe_to_move = True
            else:
                return

        thread = Thread(target=test.run_test, args=(self.axis,))
        thread.daemon = True
        thread.start()
        for t in self.test_buttons:
            t.configure(state=DISABLED)
        test.running.trace("w", lambda *args: self.events.put(self.enable_buttons))

    def toggle_connection(self):
        if self.connection_open:
            self.log("Closing connection")
            for t in self.test_buttons:
                t.configure(state=DISABLED)
            self.stop_button.configure(state=DISABLED)
            new_text = "Reconnect"
            self.g.GClose()
        else:
            self.log("Opening new connection")
            self.stop_button.configure(state=NORMAL)
            self.test_buttons[0].configure(state=NORMAL)
            new_text = "Disconnect"
            open_connection(self.g)

        self.disconnect_button.configure(text=new_text)
        self.connection_open = not self.connection_open

    def create_widgets(self):
        self._create_test_button(DirectionTest, NORMAL)

        self._create_test_button(EncoderTest)

        self._create_test_button(BacklashTest)

        self._create_test_button(RepeatabilityTest)

        self.axis.limits_found.trace("w", lambda *args: self.events.put(self.enable_buttons))

        self.stop_button = Button(self, text="STOP MOTORS", command=self.manual_stop, bg='#FF0000')
        self._place_button(self.stop_button)

        self.disconnect_button = ttk.Button(self, text="Disconnect", command=self.toggle_connection)
        self._place_button(self.disconnect_button)

        self._place_button(ttk.Button(self, text="Save All Axes Setup", command=self.parent.save_setup))

        self._place_button(ttk.Button(self, text="Load All Axes Setup", command=self.parent.load_setup))

        self._place_button(ttk.Button(self, text="Exit", command=self.parent.quit))
