#!/usr/bin/env python

import arduino
from multiprocessing import Process
from btconnection import *
import time

# define paired devices
devices_paired = [
    ('F8:E0:79:C2:C3:CE', 'Moto G', 1),
    ('F8:E0:79:C2:C3:CE', 'Moto G', 6),
    ('30:14:09:29:31:73', 'HC-06', 1)
]

# global variables
running = False  # control if infinite loops is running
Controller = None  # gamepad
# variables processes
p1 = None
p2 = None


def callback(e):
    """ Callback controller events
    every new events from controller will call this function
    """
    # concat event string and encode
    send = "<{},{}>".format(e.code, e.state).encode('ascii')
    # send to bluetooth
    print('Out:', send)  # ArduinoBT.tx(send)


def sock_receive():
    """ Loop for Bluetooth Read """
    while running:
        time.sleep(0.1)  # sleep 100ms
        # nem vai funcionar sem BT # ArduinoBT.rx()


def sock_transmit():
    """ Loop for Bluetooth Write """
    while running:
        time.sleep(0.002)  # sleep 2ms
        Controller.check_events(callback)


try:
    # show table with devices
    print_table(devices_paired)

    # device = choose(devices_paired)
    # btsock = do_connection(*device)
    # ArduinoBT = arduino.Bluetooth(device)  # create connection

    # controller
    Controller = arduino.XduinoController()  # convert xbox controller events in arduino commands
    Controller.ndigits = 2
    Controller.lratio = 0.5
    Controller.rratio = 0.8
    Controller.m1scale = 255
    Controller.m2scale = 255

    print("\nReadyyyyyyy...")
    time.sleep(1)  # wait some seconds to estabilize connection
    print("Gooo!")

    running = True
    # run bluetooth read and write in parallel
    p1 = Process(target=sock_transmit)
    # p2 = Process(target=sock_receive)
    # start processes
    p1.start()
    # self.p2.start()
    # stop code util all processes are finish
    p1.join()
    # self.p2.join()

except OSError:
    # controller disconnect
    print("Connection lost. Reconnecting ...")
    time.sleep(3)  # sleep waiting connection

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    p1.terminate()
    # self.p2.terminate()
    print("\nBye bye!")
    exit()
