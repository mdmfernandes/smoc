# -*- coding: utf-8 -*-
"""Optimizer root module"""

from __future__ import print_function

import socket
import sys

from utils.file import read_yaml


def main():
    """The main!"""

    # Support Python 2 and 3 input (default to Python 3's input())
    get_input = input

    # If this is Python 2, use raw_input()
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input

    print("Connecting...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            server = read_yaml()['server']

            s.connect((server['host'], server['port']))

            data = s.recv(1024).decode('utf8')
            
            print("Connected to server with the address", data)
            print("Sending 'DONE' shuts down the server and quits.")

            while True:
                try:
                    x = get_input("py> ")
                    if x != "":
                        print("SEND:", x)
                        s.sendall(x.encode('utf8'))

                        if x.upper() == "DONE":
                            print("Shutting down.")
                            break
                except KeyboardInterrupt:
                    print("Shutting down.")

                data = s.recv(1024).decode('utf8')
                print('Data received from pys: %s' % data)

    except OSError as err:
        print("Error: {0}".format(err))
        print("Check if server is running and try again...!")
    else:
        print("END OF CLIENT")


if __name__ == "__main__":
    main()
