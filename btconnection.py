#!/usr/bin/env python

import bluetooth


def find_devices():
    print('Looking for nearby devices...')

    return bluetooth.discover_devices(
        duration=5,
        lookup_names=True,
        flush_cache=True,
        lookup_class=False
    )


def find_services():
    print('Looking for nearby services...')
    services = bluetooth.find_service()
    services_list = []

    for s in services:
        services_list.append((s['host'], str(s['name'])))

    return services_list


def print_table(*args):
    # table header
    print("\n{:2} {:18} {}".format('ID', 'ADDRESS', 'NAME'))

    # create a table with all devices
    i = 0  # counter

    for devices in args:
        if len(devices):
            for addr, name in devices:
                i += 1  # increment
                try:
                    print('{:2} {:18} {:}'.format(i, addr, name))
                except UnicodeEncodeError:
                    print('{:2} {:18} {:}'.format(
                        i, addr, name.encode('utf-8', 'replace'))
                    )

            print(' ------------------------------ ')  # separator
        else:
            print(' ----------- EMPTY ------------ ')


# start define devices
devices_nearby = find_services()
devices_paired = [
    ('F8:E0:79:C2:C3:CE', 'Moto G'),
    ('30:14:09:29:31:73', 'HC-06')
]

# show table with devices
print_table(devices_paired, devices_nearby)
# join lists
devices = devices_paired + devices_nearby

# selection of the device to connect
print("\nType device ID to connect:", end=" ")
choice = int(input().lower()) - 1
addr = devices[choice][0]
name = devices[choice][1]
running = True

print("connecting to \"%s\" on %s" % (name, addr))
exit()

# TODO
# Create the client socket
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((addr, 1))

print("connected.\n")

try:
    while running:
        data_recv = sock.recv(1024)
        print("received [%s]" % data_recv)

        data_send = input()

        if data_send == "quit":
            raise KeyboardInterrupt
        sock.send(data_send.encode('ascii'))

except (KeyboardInterrupt, EOFError):
    # error rise or Ctrl+C is pressed
    running = False
    sock.close()
    print("\nBye bye!")
