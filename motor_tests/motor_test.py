from Tkinter import BooleanVar
from functools import partial
import tkMessageBox


class MotorTest():
    def __init__(self, event_queue, logger, name):
        self.name = name
        self.event_queue = event_queue
        self.log = logger
        self.running = BooleanVar()

    def _error_handler(self, exception):
        tkMessageBox.showerror("Error", exception.message)

    def run(self):
        self.running.set(True)
        try:
            self.perform_test()
        except Exception as e:
            err_handler = partial(self._error_handler, e)
            self.event_queue.put(err_handler)
        self.log("{} Finished".format(self.name))
        self.running.set(False)

    def get_settings_ui(self, frame):
        pass

    def perform_test(self):
        pass