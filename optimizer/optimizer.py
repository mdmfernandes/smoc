#!/usr/bin/python
# -*- coding: utf-8 -*-

# atenção que a sintaxe no python 3 é diferente!!
# ver: https://docs.python.org/3/library/socket.html#example

import sys
import socket
import os
import os.path
import subprocess
import time
import signal

if len(sys.argv) == 2 and sys.argv[1] == 'cad':
    # open skill process
    CAD = subprocess.Popen(['gnome-terminal', '-x', 'icfb', '-nograph', '-restore', 'cadence.il'])
    time.sleep(12)
	

print("Connecting...")
if os.path.exists("/tmp/pythcad_socket"):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect("/tmp/pythcad_socket")
    print("Ready.")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
        try:
            x = raw_input("py> ") # no python 3.x é "input"
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
