# -*- coding: utf-8 -*-
"""Client that communicates with Cadence through the server"""

import socket
import sys


class Client(object):
    """A client that handles Cadence requests.

    This client receives data from Cadence (through a server) and processes that data.
    It then gather the results and send them back to Cadence.

    Arguments:
        host {string} -- host IP address
        port {integer} -- host PORT
    """

    def __init__(self, host, port):
        """Start the client"""

        self.host = host
        self.port = port

        try:    # Try to create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:    # Try to connect to server
                print("Connecting to server...")
                self.socket.connect((host, port))

                local_sockname = str(self.socket.getsockname())

                # Send the local socket name to the server
                self.socket.sendall(local_sockname.encode())

                # Receive the remote socket name
                remote_sockname = self.socket.recv(1024).decode('utf8')

                print("Connected to server with the address", remote_sockname)
                print("Sending 'DONE' shuts down the server and quits.")

            except:
                print("Connect Exception")
                self.socket.close()
                raise   # Re-raise this error to call the outter except

        except:
            print("Socket Exception")
            raise       # Re-raise this error to call the except of the main

    def run(self):
        """Run the client: Send and receive data to/from server"""

        while True:
            try:
                x = input("py> ")
                if x != "":
                    print("SEND:", x)

                    self.socket.sendall(x.encode('utf8'))

                    if x.upper() == "DONE":
                        print("Shutting down.")
                        break
            except:
                print("Keyboard Interrupt")
                raise

            data = self.socket.recv(1024).decode('utf8')
            print('Data received from pys: {}'.format(data))

        self.socket.close() # Close the socket
        print("--- END OF CLIENT ---")

    @staticmethod
    def process_request(req):
        # TODO
        return req

    @staticmethod
    def process_response(res):
        # TODO
        return res
