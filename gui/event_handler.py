import Queue
from threading import Lock, Thread


class EventHandler():
    lock = Lock()
    in_queue = Queue.Queue()
    out_queue = Queue.Queue()

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
        self.in_queue.put(func)

    def process_queue(self):
        with self.lock:
            while not self.in_queue.empty():
                try:
                    func = self.in_queue.get(0)
                    returned = func()
                    if returned is not None:
                        self.out_queue.put(returned)
                except Queue.Empty:
                    pass
            self.root.after(100, self.process_queue)