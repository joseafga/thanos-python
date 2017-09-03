#!/usr/bin/env python

from multiprocessing import Process
from gamepad import XboxController
from btconnection import *
import time

# define paired devices
devices_paired = [
    ('F8:E0:79:C2:C3:CE', 'Moto G', 1),
    ('F8:E0:79:C2:C3:CE', 'Moto G', 8),
    ('30:14:09:29:31:73', 'HC-06', 1)
]
# show table with devices
print_table(devices_paired)

device = choose(devices_paired)
btsock = do_connection(*device)
Controller = XboxController()
prev_event = None
running = True


def callback(e):
    """ Callback controller events
    every new events from controller will call this function
    """
    global prev_event  # previus event
    event = (e.code, round(e.state, 2))  # current event

    # prevent send same event after round
    if prev_event == event:
        return

    # update prev event and continue to send via bluetooth
    prev_event = event
    # concat event string and encode
    send = "{},{}\n".format(event).encode('ascii')
    # send to bluetooth
    btsock.send(send)
    print('Out:', send)


def sock_read():
    """ Loop for Bluetooth Read """
    while running:
        time.sleep(0.1)  # sleep 100ms

        read = btsock.recv(1024)
        print('In:', read)


def sock_write():
    """ Loop for Bluetooth Write """
    while running:
        time.sleep(0.002)  # sleep 2ms
        Controller.check_events(callback)


# run bluetooth read and write in parallel
try:
    p1 = Process(target=sock_read)
    p2 = Process(target=sock_write)
    # start processes
    p1.start()
    p2.start()
    # stop code util all processes are finish
    p1.join()
    p2.join()

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    btsock.close()
    p1.terminate()
    p2.terminate()
    print("\nBye bye!")
