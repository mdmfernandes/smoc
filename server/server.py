#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

# The first line is a shebang to execute the server from shell (./)

"""Server that stands between the optimizer and cadence."""

import socket
import sys
import time


class Server(object):
    """A server that handles skill commands.

    This server is started and ran by cadence. It listens for commands from the optimizer
    from a TCP socket, then pass the command to cadence. It then gather the result and
    send it back to the optimizer.

    Arguments:
        cad_file {file} -- cadence stream

    Keyword Arguments:
        is_cadence {boolean} -- if true, the server was started from cadence (default: {True})
        debug {boolean} -- if true send debug messages to cadence (default: {False})
    """

    HOST = 'localhost'
    PORT = 3000

    def __init__(self, cad_file, is_cadence=True, debug=False):
        """Create a new Server instance."""

        self.cad_file = cad_file
        self.server_in = self.cad_file.stdin
        self.server_out = self.cad_file.stdout
        self.server_err = self.cad_file.stderr
        self.is_cadence = is_cadence
        self.debug = debug

    def run(self):
        """Start the server."""

        if self.is_cadence:
            # Receive initial message from cadence, to check connectivity
            # TODO: METER AQUI UM TRY!!!
            msg = self.recv_skill()

            self.send_skill(msg)
        else:
            print("Starting server...")

        try:
            # Start connection between the optimizer and the server (UNIX socket)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # define socket options to allow the reuse of the same addr
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Start to listen to the socket
                s.bind((Server.HOST, Server.PORT))
                s.listen(1)

                # Waits for client connection
                conn, addr = s.accept()

            with conn:
                # Receive socket info from client
                sockname = conn.recv(1024).decode()

                if not self.is_cadence:
                    print("Client host:", sockname)

                conn.sendall(str(addr).encode('utf8'))

                if self.is_cadence:
                    self.send_skill(str(addr))

                    self.recv_skill()

                    if self.debug is True:
                        self.send_debug(
                            str('Client is connected to address ' + addr))

                while True:
                    # Receive request from the optimizer
                    # TODO: Meter assíncrono
                    req = conn.recv(1024).decode('utf8')

                    #print("Received: ", req)

                    # Check for request to end connection
                    if req.upper() == "DONE":
                        break

                    if self.is_cadence:
                        # Process the optimizer request
                        #expr = self.process_skill_request(req)

                        expr = req

                        # Send the request to Cadence
                        self.send_skill(expr)

                        # Wait for the response from Cadence
                        #msg = self.recv_skill()

                        if self.debug is True:
                            self.send_debug('Data sent to client: %s' % msg)

                        # Process the Cadence response
                        obj = self.process_skill_response(req)
                    else:
                        print("Received data:", req)
                        obj = req

                    # Send the message to the optimizer
                    conn.sendall(obj.encode('utf-8'))

        # except (OSError, AttributeError, IOError) as err:
            #print("Error: {0}".format(err))
        except:
            #print("Error: ", sys.exc_info()[0])
            self.send_warn("my Error: {}".format(sys.exc_info()))

        finally:
            self.close()    # Stop the server

    def send_skill(self, expr):
        """Send a skill expression to Cadence for evaluation.

        Arguments:
            data {string} -- skill expression
        """
        self.server_out.write(expr)
        self.server_out.flush()

    def recv_skill(self):
        """Receive a response from Cadence.

        First receives the message length (number of bytes) and then receives the message

        Returns:
            msg {string} -- message received from cadence
        """
        num_bytes = int(self.server_in.readline())
        msg = self.server_in.read(num_bytes)

        # Remove the '\n' from the message
        if msg[-1] == '\n':
            msg = msg[:-1]

        return msg

    def send_warn(self, warn):
        """Send a warning message to Cadence.

        Arguments:
            warn {string} -- warning message
        """
        self.server_err.write(warn)
        self.server_err.flush()

    def send_debug(self, msg):
        """Send a debug message to Cadence.

        Arguments:
            msg {string} -- debug message
        """

        time.sleep(1)
        self.send_warn(msg)

    def process_skill_request(self, req):
        """Process a skill request from the optimizer.

        Based on the given request object, returns the skill expression
        to be evaluated by Cadence.

        Arguments:
            req {dict} -- request object

        Returns:
            expre {string or None} -- expression to be evaluated by Cadence
        """
        # TODO: for now it's just a string
        expr = req

        return expr

    def process_skill_response(self, msg):
        """Process the skill response from Cadence.

        Arguments:
            msg {string} -- cadence response

        Returns:
            obj {dict} -- response object
        """

        # TODO: for now it's just a string
        obj = str(msg)

        return obj

    def close(self):
        """Close this server."""

        # Send feedback to Cadence
        self.send_warn("Connection with the optimizer ended!\n\n")
        self.server_out.close()  # close stdout
        self.server_err.close()  # close stderr
        self.cad_file.exit(255)  # close connection to cadence (code up to 255)


def start_server():
    """Start the server"""

    # Check call argumments
    is_cadence = (len(sys.argv) != 2)

    print(is_cadence)

    server = Server(sys, is_cadence, debug=False)
    server.run()


if __name__ == "__main__":
    start_server()
