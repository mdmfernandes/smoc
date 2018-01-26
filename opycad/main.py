#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimizer root module"""

import sys

from util.file import read_yaml
from interface.client import Client
from interface.menu import print_menu

def start_simulator():
    pass

def update_and_run():
    pass


def main():
    """Optimizer main function"""
    # Load server host, port
    server = read_yaml()['server']
    host = server['host']
    port = server['port']

    # Start the client
    try:
        client = Client(host, port)
    except (OSError, KeyboardInterrupt) as err:
        print("ClientError: {0}".format(err))
        return 0

    # Program loop
    while True:
        try:
            option = print_menu()

            if not option:  # if option == 0
                print("Shutting down.")
                data = dict(type='info', data='exit')
                client.send_data(data)
                break
            elif option == 1:
                data = dict(type='loadSimulator', data='ola')
            elif option == 2:
                data = dict(type='updateAndRun', data='updateAndRun')
            else:
                raise RuntimeError("Nunca devia ter chegado aqui!!!")

            client.send_data(data)

            #
            # Wait for data from server
            #
            data = client.recv_data()
            data = data['data']
            print('Data received from pys: {}'.format(data))

        except:
            print(f"my Error: {sys.exc_info()}")
            raise

    client.close()  # Close the socket
    print("--- END OF CLIENT ---")


if __name__ == "__main__":
    main()
