import Queue
from threading import Lock


class EventHandler():
    lock = Lock()
    in_queue = Queue.Queue()

    def __init__(self, root):
        self.root = root
        root.after(100, self.process_queue)

    def put(self, func):
        self.in_queue.put(func)

    def process_queue(self):
        with self.lock:
            while not self.in_queue.empty():
                try:
                    func = self.in_queue.get(0)
                    func()
                except Queue.Empty:
                    pass
            self.root.after(100, self.process_queue)