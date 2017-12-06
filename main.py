#!/usr/bin/env python

from time import sleep
from btconnection import *
import arduino

# define paired devices
devices_paired = [
    ('F8:E0:79:C2:C3:CE', 'Moto G', 8),
    ('F8:E0:79:C2:C3:CE', 'Moto G', 7),
    ('F8:E0:79:C2:C3:CE', 'Moto G', 6),
    ('30:14:09:29:31:73', 'HC-06', 1)
]
# some options
WAIT_TIME = 5
AUTO_RECONNECT = 1
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
        sleep(WAIT_TIME)  # sleep waiting connection

        # if sync ok break loop
        if Controller.sync():
            print(" Done.")
            break


def bluetooth_sync():
    if not AUTO_RECONNECT:
        return

    try:
        sleep(WAIT_TIME)  # sleep waiting connection
        arduinoBT.reconnect()
    except Exception as e:
        print("Can't connect ... trying again")
        bluetooth_sync()


def callback(e):
    """ Callback controller events
    every new events from controller will call this function
    """
    # concat event string and encode
    send = "<{},{}>".format(e.code, e.state).encode('ascii')
    # send to bluetooth
    arduinoBT.tx(send)


def sock_receive(q):
    """ Loop for Bluetooth Read """
    try:
        while running:
            sleep(0.5)  # sleep 500ms
            arduinoBT.rx()

    except bluetooth.btcommon.BluetoothError as e:
        q.put("Bluetooth receive error.")
        pass

    except Exception as e:
        print("Generic error on receive")
        for x in e.args:
            print("error: ", x)


def sock_transmit(q):
    """ Loop for Bluetooth Write """
    try:
        while running:
            sleep(0.002)  # sleep 2ms
            Controller.check_events(callback)

    except FileNotFoundError as e:
        controller_sync("Lost controller, resynchronizing")
        sock_transmit()  # back to process

    except bluetooth.btcommon.BluetoothError as e:
        q.put("Bluetooth transmit error.")

    except Exception as e:
        print("Generic error on transmit")
        for x in e.args:
            print("error: ", x)


try:
    # show table with devices
    print_table(devices_paired)
    device = choose(devices_paired)
    # start preparations
    print("\nPreparing...")
    # create bluetooth connection
    arduinoBT = arduino.Bluetooth(device)
    # xbox controller
    controller_sync("synchronizing controller")
    running = True
    print("Gooo!")  # all done

    # run bluetooth processes
    while running:
        # create processes to read and write in parallel
        arduinoBT.start((sock_receive, sock_transmit))
        print(arduinoBT.get_errors(), "Reconnecting ...")  # wait for error
        arduinoBT.stop()
        bluetooth_sync()

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    arduinoBT.stop()
    print("\nBye bye!")
