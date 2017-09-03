#!/usr/bin/env python

import bluetooth


def find_devices():
    print('Looking for nearby devices...')
    devices_list = []

    devices = bluetooth.discover_devices(duration=5, lookup_names=True)
    for d in devices:
        devices_list.append(d + (1,))

    return devices_list


def find_services():
    print('Looking for nearby services...')
    services = bluetooth.find_service()
    services_list = []

    for s in services:
        services_list.append((s['host'], str(s['name']), s['port']))

    return services_list


def print_table(*args):
    # table header
    print("\n{:2} {:<18} {:<4} {}".format('ID', 'ADDRESS', 'PORT', 'NAME'))

    # create a table with all devices
    i = 0  # counter

    for devices in args:
        if len(devices):
            for device in devices:
                i += 1  # increment
                addr, name, port = device

                print('{:>2} {:<18} {:<4} {}'.format(i, addr, port, name))

            print(' ------------------------------ ')  # separator
        else:
            print(' ----------- EMPTY ------------ ')
    else:
        print('{:2} Find Devices'.format(i + 1))
        print('{:2} Find Services'.format(i + 2))
        print(' ------------------------------ ')


def choose(devices):
    print("\nType device ID or action:", end=" ")
    choice = int(input().lower())

    diff = choice - len(devices)

    if diff > 0:
        if diff == 1:
            devices_nearby = find_devices()
            print_table(devices_nearby)
            return choose(devices_nearby)
        else:
            services_nearby = find_services()
            print_table(services_nearby)
            return choose(services_nearby)

    return devices[choice - 1]


def do_connection(addr, name, port):
    # show message
    print("Connecting to {} on {} port {}".format(name, addr, port))

    # Create the client socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((addr, port))

    # connection ok
    print("Connected.\n")

    return sock
