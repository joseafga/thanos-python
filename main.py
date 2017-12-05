#!/usr/bin/env python

import arduino
from btconnection import *
import time

# define paired devices
devices_paired = [
    ('F8:E0:79:C2:C3:CE', 'Moto G', 1),
    ('F8:E0:79:C2:C3:CE', 'Moto G', 6),
    ('30:14:09:29:31:73', 'HC-06', 1)
]
# some options
WAIT_TIME = 1
# global variables
running = False  # control if infinite loops is running
# variables processes
p1 = None
p2 = None
# controller and their options
Controller = arduino.XduinoController()  # convert xbox controller events in arduino commands
Controller.ndigits = 2
Controller.lratio = 1
Controller.rratio = 1
Controller.m1scale = 255
Controller.m2scale = 255


def controller_sync(msg):
    """ Loop for controller connection """
    print(msg, end="..")

    while True:
        print(".", end='', flush=True)  # print new . for every attempt
        time.sleep(WAIT_TIME)  # sleep waiting connection

        # if sync ok break loop
        if Controller.sync():
            print(" Done.")
            break


def callback(e):
    """ Callback controller events
    every new events from controller will call this function
    """
    # concat event string and encode
    send = "<{},{}>".format(e.code, e.state).encode('ascii')
    # send to bluetooth
    ArduinoBT.tx(send)


def sock_receive():
    """ Loop for Bluetooth Read """
    while running:
        time.sleep(0.1)  # sleep 100ms
        ArduinoBT.rx()


def sock_transmit():
    """ Loop for Bluetooth Write """
    try:
        while running:
            time.sleep(0.002)  # sleep 2ms
            Controller.check_events(callback)
    except (OSError, FileNotFoundError) as e:
        controller_sync("Lost controller, resynchronizing")
        sock_transmit()  # back to process


try:
    # show table with devices
    print_table(devices_paired)
    device = choose(devices_paired)
    # btsock = do_connection(*device)
    ArduinoBT = arduino.Bluetooth(device)  # create connection

    # start preparations
    print("\nPreparing...")
    controller_sync("synchronizing controller ...")
    running = True
    print("Gooo!")  # all done

    # run bluetooth read and write in parallel
    ArduinoBT.start(sock_receive, sock_transmit)

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    ArduinoBT.stop()
    print("\nBye bye!")
