#!/usr/bin/env python

# connection: socat -d -d pty,raw,echo=0 pty,raw,echo=0
# listen: cat < /dev/pts/2
# write: echo "string" > /dev/pts/2

from multiprocessing import Process
from gamepad import XboxController
import serial
import time

ser = serial.Serial('/dev/pts/3', 9600)  # 10ms for read
Controller = XboxController()
running = True


def handle(event):
    """ Handle controller events
    every new events from controller will exec this function
    """
    ser.write((event.code + " - " + str(event.state)).encode("UTF-8"))
    print(event.code, event.state)


def serial_read():
    global running
    readline = ""

    while running:
        time.sleep(0.01)  # sleep 10ms

        read = ser.read()
        if read:
            if read == b"\n":
                print(readline)
                readline = ""
            else:
                readline += read.decode("UTF-8")


def serial_write():
    global running

    while running:
        time.sleep(0.001)  # sleep 10ms
        Controller.refresh_events(handle)


# run serial read and write in parallel
try:
    p1 = Process(target=serial_read)
    p2 = Process(target=serial_write)
    # start processes
    p1.start()
    p2.start()
    # stop code util all processes are finish
    p1.join()
    p2.join()

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    p1.terminate()
    p2.terminate()
    print("\nBye bye!")
