#!/usr/bin/env python

from multiprocessing import Process
from btconnection import *
import gamepad


class Bluetooth:
    btsock = None

    def __init__(self, device):
        self.btsock = do_connection(*device)

    def rx(self):
        read = self.btsock.recv(1024)
        print('In:', read)

        return read

    def tx(self, data):
        self.btsock.send(data)
        print('Out:', data)

        return True

    def start(self, receive, transmit):
        self.p1 = Process(target=receive)
        self.p2 = Process(target=transmit)
        # start processes
        self.p1.start()
        self.p2.start()
        # stop code util all processes are finish
        self.p1.join()
        self.p2.join()

    def stop(self):
        self.btsock.close()
        self.p1.terminate()
        self.p2.terminate()


class XduinoController(gamepad.XboxController):
    # right and left ratio
    # use for a side turn more or less .. can reduce total turn too
    rratio = 1
    lratio = 1
    # motors scale
    m1scale = 1023
    m2scale = 1023

    def __init__(self, *args, **kwargs):
        super(XduinoController, self).__init__(*args, **kwargs)

    def translate(self, callback=False, *args, **kwargs):
        self.prev_callback = callback  # store previous callback
        # call parent method with new callback
        super(XduinoController, self).check_events(callback=self.command, *args, **kwargs)

    def command(self, event):
        """  This will translate controller event to Arduino command """
        if event.code in ["LZ", "RZ", "LX"]:
            # rewrite event for accelerate and turn
            m1 = m2 = round(self.prev.get("RZ", 0) - self.prev.get("LZ", 0), self.ndigits)
            turn = self.prev.get("LX", 0)
            if (turn > 0):  # right
                m1 *= (1 - turn * self.rratio)
            elif (turn < 0):  # left
                m2 *= (1 - abs(turn) * self.lratio)

            state = str(round(m1 * self.m1scale)) + "," + str(round(m2 * self.m2scale))

            event.code = "MP"
            event.state = state

        elif event.code == "DX":
            # turn on self axis
            m1 = event.state
            m2 = event.state * -1
            state = str(round(m1 * self.m1scale)) + "," + str(round(m2 * self.m2scale))

            event.code = "MP"
            event.state = state

        elif event.code in ["BM"]:
            ...

        else:
            # useless event, just skip
            return

        # check if prev event is the same
        if self.prev.get(event.code) == event.state:
            return
        self.prev[event.code] = event.state

        # call previous callback if it exists
        if callable(self.prev_callback):
            self.prev_callback(event)
            self.prev_callback = None  # clean after exec
