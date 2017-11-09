import time
import random


class MockGalil():
    arr_num = 0

    def __init__(self, log):
        self.log = log

    def GOpen(self, port):
        print("Opening on {}".format(port))

    def GInfo(self):
        return "string"

    def GProgramDownload(self, program, opt):
        if program == "":
            self.log("Wiping Program")
        else:
            self.log("Downloading: {}".format(program))

    def GCommand(self, to_send):
        self.log("Sending {}".format(to_send))
        return ""

    def GMotionComplete(self, axis):
        time.sleep(0.5)
        self.log("Waiting for motion on {}".format(axis))

    def GArrayUpload(self, name, start, end):
        if end == -1:
            end = 4000

        out = []
        for i in range(start, end):
            start = self.arr_num*10
            out.append(random.randint(start, start+10))
        self.log("Uploading array: {}".format(out[0:5]))
        self.arr_num += 1
        return out

    def GClose(self):
        self.log("Closing connection")
