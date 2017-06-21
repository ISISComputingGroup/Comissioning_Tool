import time
import random


class MockGalil():
    def __init__(self, log):
        self.log = log

    def GOpen(self, port):
        print "Opening on {}".format(port)

    def GInfo(self):
        return "string"

    def GProgramDownload(self, program, opt):
        if program == "":
            self.log("Wiping Program")
        else:
            self.log("Downloading: {}".format(program))

    def GCommand(self, to_send):
        self.log("Sending {}".format(to_send))

    def GMotionComplete(self, axis):
        time.sleep(2)
        self.log("Waiting for motion on {}".format(axis))

    def GArrayUpload(self, name, start, end):
        if end == -1:
            end = 4000
        out = []
        for i in range(start, end):
            out.append(random.randint(0, 1000))
        self.log("Uploading array: {}".format(out[0:5]))
        return out

    def GClose(self):
        self.log("Closing connection")