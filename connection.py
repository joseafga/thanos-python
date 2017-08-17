#!/usr/bin/env python

# connection: socat -d -d pty,raw,echo=0 pty,raw,echo=0
# listen: cat < /dev/pts/2
# write: echo "string" > /dev/pts/2

from multiprocessing import Process
from gamepad import XboxController
import serial
import time

ser = serial.Serial('/dev/pts/4', 9600)  # 10ms for read
Controller = XboxController()
running = True


def callback(e):
    """ Callback controller events
    every new events from controller will call this function
    """
    # concat event string and encode
    send = "{},{}\n".format(e.code, e.state).encode('ascii', 'replace')
    # send as serial
    ser.write(send)
    print('Out:', send)


def serial_read():
    """ Loop for Serial Read """
    global running
    readline = ""

    while running:
        time.sleep(0.01)  # sleep 10ms

        read = ser.read()
        if read:
            if read == b"\n":
                print('In:', readline)
                readline = ""
            else:
                readline += read.decode('ascii')


def serial_write():
    """ Loop for Serial Write """
    global running

    while running:
        time.sleep(0.001)  # sleep 10ms
        Controller.check_events(callback)


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
