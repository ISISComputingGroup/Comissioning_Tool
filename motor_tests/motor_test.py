from tkinter import messagebox, BooleanVar
from functools import partial


class MotorTest():
    """
    An interface for a generic test to be performed on an axis.
    """
    def __init__(self, axis, event_queue, logger):
        self.event_queue = event_queue
        self.log = logger
        self.running = BooleanVar()
        self.axis = axis

    def _error_handler(self, exception):
        messagebox.showerror("Error", exception.message)

    def run_test(self, axis):
        self.running.set(True)
        self.axis = axis
        try:
            self.perform_test()
        except Exception as e:
            err_handler = partial(self._error_handler, e)
            self.event_queue.put(err_handler)
        finally:
            self.axis.stop()
        self.log("{} Finished".format(self.name))
        self.running.set(False)
