# -*- coding: utf-8 -*-

"""Server that stands between the optimizer and cadence."""

import socket
import sys
import time


class Server(object):
    """A server that handles skill commands.

    This server is started and ran by cadence. It listens for commands from the optimizer
    from a UNIX socket, then pass the command to cadence. It then gather the result and
    send it back to the optimizer.

    Arguments:
        cad_file {file} -- cadence stream

    Keyword Arguments:
        debug {boolean} -- if true send debug messages to cadence(default: {False})
    """

    HOST = 'localhost'
    PORT = 3000

    def __init__(self, cad_file, debug=False):
        """Create a new Server instance."""

        self.cad_file = cad_file
        self.cad_in = self.cad_file.stdin
        self.cad_out = self.cad_file.stdout
        self.cad_err = self.cad_file.stderr
        self.debug = debug

    def run(self):
        """Start the server."""

        # Receive initial message from cadence, to check connectivity
        # TODO: METER AQUI UM TRY!!!
        # msg = self.recv_skill()

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

                print("Connected to the client: ", addr)

            with conn:
                # Forwards the message received from Cadence
                # conn.sendall(msg)
                conn.sendall(str(addr).encode('utf8'))

                if self.debug is True:
                    self.send_debug(
                        str('Client is connected to address ' + addr))

                while True:
                    # Receive request from the optimizer
                    # TODO: Meter assíncrono
                    req = conn.recv(1024).decode('utf8')

                    print("Received: ", req)

                    # Check for request to end connection
                    if req.upper() == "DONE":
                        break

                    # Process the optimizer request
                    #expr = self.process_skill_request(req)

                    # Send the request to Cadence
                    # self.send_skill(expr)

                    # Wait for the response from Cadence
                    #msg = self.recv_skill()

                    if self.debug is True:
                        self.send_debug('Data sent to client: %s' % msg)

                    # Process the Cadence response
                    obj = self.process_skill_response(req)

                    # Send the message to the optimizer
                    conn.sendall(obj.encode('utf-8'))

        #except (OSError, AttributeError, IOError) as err:
            #print("Error: {0}".format(err))
        except:
            print("Error: ", sys.exc_info()[0])
        finally:
            self.close()    # Stop the server

    def send_skill(self, expr):
        """Send a skill expression to Cadence for evaluation.

        Arguments:
            data {string} -- skill expression
        """
        self.cad_in.write(expr)
        self.cad_in.flush()

    def recv_skill(self):
        """Receive a response from Cadence.

        First receives the message length (number of bytes) and then receives the message

        Returns:
            msg {string} -- message received from cadence
        """
        num_bytes = int(self.cad_out.readline())
        msg = self.cad_out.read(num_bytes)

        # Remove the '\n' from the message
        if msg[-1] == '\n':
            msg = msg[:-1]

        return msg

    def send_warn(self, warn):
        """Send a warning message to Cadence.

        Arguments:
            warn {string} -- warning message
        """
        self.cad_err.write(warn)
        self.cad_in.flush()

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
        obj = msg

        return obj

    def close(self):
        """Close this server."""

        # Send feedback to Cadence
        self.send_warn("Connection with the optimizer ended!\n\n")
        self.cad_out.close()  # close stdout
        self.cad_err.close()  # close stderr
        self.cad_file.exit(255)  # close connection to cadence (code up to 255)


def start_server():
    """Start the server"""

    server = Server(sys, debug=False)
    server.run()


if __name__ == "__main__":
    start_server()
