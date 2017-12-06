#!/usr/bin/env python

from multiprocessing import Process, Queue
from btconnection import *
import gamepad


class Bluetooth:
    btsock = None
    device = None
    connected = False

    def __init__(self, device):
        self.btsock = do_connection(*device)
        # store connected device
        self.device = device
        self.connected = True

    def reconnect(self):
        self.btsock = do_connection(*self.device)
        self.connected = True

    def disconnect(self):
        self.btsock.close()
        self.connected = False

    def rx(self):
        # read data from BT sock
        read = self.btsock.recv(1024)
        print('In:', read)

        return read

    def tx(self, data):
        # send data via BT sock
        self.btsock.send(data)
        print('Out:', data)

        return True

    def get_errors(self):
        # return errors from queue
        return self.queue.get()

    def start(self, fx):
        # queue used to pass errors
        self.queue = Queue()
        # store all processes started
        self.processes = []
        # create and start processes
        for f in fx:
            p = Process(target=f, args=(self.queue,))
            self.processes.append(p)
            p.start()

    def stop(self):
        # disconect from sock and terminate processes
        self.disconnect()
        for p in self.processes:
            p.terminate()


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
