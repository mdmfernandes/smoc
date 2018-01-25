#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimizer root module"""

from util.file import read_yaml
from interface.client import Client
from interface.menu import print_menu


def run_client():
    """Run the client: Send and receive data to/from server"""


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

    # Program loop
    while True:
        try:
            x = input("py> ")
            if x != "":
                print("SEND:", x)

                client.send_data(dict(type='info', data=x))

                if x.upper() == "DONE":
                    print("Shutting down.")
                    break
        except:
            print("Keyboard Interrupt")
            raise

        data = client.recv_data()
        data = data['data']
        print('Data received from pys: {}'.format(data))

    client.close()  # Close the socket
    print("--- END OF CLIENT ---")


if __name__ == "__main__":
    main()
