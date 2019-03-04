#!/usr/bin/env python

from multiprocessing import Process, Queue
from btconnection import *
import gamepad
import signal


class Bluetooth:
    btsock = None
    timeout = 10
    countdown = 1
    device = None
    connected = False
    prev = b'<M,0,0>'  # start with some command

    def __init__(self, device):
        # store connected device
        self.device = device

    def connect(self):
        self.btsock = do_connection(*self.device)
        if self.timeout > 0:
            self.btsock.settimeout(self.timeout)
        self.connected = True

    # close bluetooth sock connection
    def disconnect(self):
        self.btsock.close()
        self.finish_countdown()
        self.connected = False

    # signal handler
    def _countdown(self, *args, **kwargs):
        self.tx(self.prev)
        self.reset_countdown()

    # initialize signal countdown
    def begin_countdown(self):
        signal.signal(signal.SIGALRM, self._countdown)
        self.reset_countdown()

    def reset_countdown(self):
        signal.alarm(self.countdown)

    def finish_countdown(self):
        signal.alarm(0)

    def rx(self):
        # read data from BT sock
        read = self.btsock.recv(2048)
        # print("In:", read)

        return read

    def tx(self, data):
        # send data via BT sock
        self.btsock.send(data)
        print('Out:', data)
        # store data sended data to use in countdown
        self.prev = data
        self.reset_countdown()

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
            state = str(round(m2 * self.m2scale)) + "," + str(round(m1 * self.m1scale))

            event.code = "M"
            event.state = state

        elif event.code in ["BM"]:
            ...  # TODO
            event.code = "C"

        elif event.code in ["BX"]:
            ...  # TODO
            event.code = "X"

        else:
            # skip unimplemented codes
            event.code, event.state = "NIL", 0

        return event
