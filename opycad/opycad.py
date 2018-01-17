# -*- coding: utf-8 -*-
"""Optimizer root module"""

from __future__ import print_function

import os
import os.path
import socket
import subprocess
import sys
import time


def main():
    """The main!"""

    # Support Python 2 and 3 input (default to Python 3's input())
    get_input = input

    # If this is Python 2, use raw_input()
    if sys.version_info[:2] <= (2, 7):
        get_input = raw_input

    # Check the input argumments
    if len(sys.argv) == 2 and sys.argv[1] == 'cad':
        # Open skill process
        cad = subprocess.Popen(
            ['gnome-terminal', '-x', 'icfb', '-nograph', '-restore', 'cadence.il'])
        time.sleep(12)  # Wait for Cadence to open and run the server

    print("Connecting...")
    if os.path.exists("/tmp/pythcad_socket"):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect("/tmp/pythcad_socket")
        print("Ready.")
        print("Ctrl-C to quit.")
        print("Sending 'DONE' shuts down the server and quits.")
        while True:
            try:
                x = get_input("py> ")
                if x != "":
                    print("SEND:", x)
                    s.sendall(x)
                    if x.upper() == "DONE":
                        print("Shutting down.")
                        break
            except KeyboardInterrupt:
                print("Shutting down.")

            data = s.recv(1024)
            print('Data received from pys: %s' % data)

        s.close()
    else:
        print("Couldn't Connect!")
    print("END OF CLIENT")


if __name__ == "__main__":
    main()
