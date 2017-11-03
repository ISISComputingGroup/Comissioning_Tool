import queue
from threading import Lock, Thread


class EventHandler():
    """
    Event handler that listens for new events to send to the UI thread.
    """
    lock = Lock()
    in_queue = queue.Queue()
    out_queue = queue.Queue()

    def __init__(self, root):
        self.root = root
        root.after(100, self.process_queue)

    def put_and_get(self, func):
        """
        This will put a function on to the ui thread and wait for a response.
        :param func: The function to run on the ui thread
        :return: The return value of the function
        """
        self.in_queue.put(func)

        return self.out_queue.get(True)

    def put(self, func):
        """
        Puts a function on to the UI thread
        :param func: The function to perform on the UI thread.
        """
        self.in_queue.put(func)

    def process_queue(self):
        """
        The function that is periodically called to check the queue for new events.
        """
        with self.lock:
            while not self.in_queue.empty():
                try:
                    func = self.in_queue.get(0)
                    returned = func()
                    if returned is not None:
                        self.out_queue.put(returned)
                except queue.Empty:
                    pass
            self.root.after(100, self.process_queue)
