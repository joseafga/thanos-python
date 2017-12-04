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
    # use for a side turn more or less than other ... never more than 1 (use scale for that)
    rratio = 1
    lratio = 1
    # motors scales ... the maximum number passed
    m1scale = 1023
    m2scale = 1023

    def __init__(self, *args, **kwargs):
        super(XduinoController, self).__init__(*args, **kwargs)

    def translate(self, event, **kwargs):
        # call parent method
        return self.command(super(XduinoController, self).translate(event, **kwargs))

    def command(self, event):
        """  This will translate controller event to Arduino command """
        if event.code in ["LZ", "RZ", "LX", "DX"]:
            # motor events
            if event.code in ["LZ", "RZ", "LX"]:
                # store event for future use
                self.prev[event.code] = event.state

                # rewrite event for accelerate and turn
                m1 = m2 = round(self.prev.get("RZ", 0) - self.prev.get("LZ", 0), self.ndigits)
                turn = self.prev.get("LX", 0)
                if (turn > 0):  # right
                    m2 *= (1 - turn * self.rratio)
                elif (turn < 0):  # left
                    m1 *= (1 - abs(turn) * self.lratio)

            elif event.code == "DX":
                # turn on self axis
                m1 = event.state
                m2 = event.state * -1

            # fix scale, round number and pass it to event var
            state = str(round(m1 * self.m1scale)) + "," + str(round(m2 * self.m2scale))

            event.code = "MP"
            event.state = state

        elif event.code in ["BM"]:
            ...  # TODO

        else:
            # skip unimplemented codes
            event.code, event.state = "NIL", 0

        return event
