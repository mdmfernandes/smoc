# This file is part of PAIM
# Copyright (C) 2018 Miguel Fernandes
#
# PAIM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAIM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# The first line is a shebang to execute the server from shell (./)
"""Server that stands between the optimizer and cadence."""

import json
import os
import socket
import struct
import sys
import time
from contextlib import contextmanager

import util


@contextmanager
def closing(thing):
    """Close stream when using the "width" since the __close__ method of
    streams is not defined in python 2.

    Arguments:
        thing {stream} -- stream (file, socket, ...)
    """
    try:
        yield thing
    finally:
        thing.close()


# pylint: disable=no-member
class Server(object):
    """A server that handles skill commands.

    This server is started and ran by cadence. It listens for commands from the optimizer
    from a TCP socket, then pass the command to cadence. It then gather the result and
    send it back to the optimizer.

    Arguments:
        cad_file {file} -- cadence stream

    Keyword Arguments:
        debug {boolean} -- if true send debug messages to cadence (default: False)
    """

    HOST = os.environ.get('PAIM_CLIENT_ADDR')
    PORT = int(os.environ.get('PAIM_CLIENT_PORT'))

    # Simulator files
    SIM_FILE = os.environ.get('PAIM_SCRIPT_PATH') + "/loadSimulator.ocn"
    RUN_FILE = os.environ.get('PAIM_SCRIPT_PATH') + "/run.ocn"

    def __init__(self, cad_file, *args):
        """Create a new Server instance."""
        self.cad_file = cad_file
        self.server_in = cad_file.stdin
        self.server_out = cad_file.stdout
        self.server_err = cad_file.stderr

        # Uninitialized variables
        self.conn = None
        self.sim_multi = None

        # Requests count
        self.count = 0

    def run(self):
        """Start the server."""
        # Receive initial message from cadence, to check connectivity
        msg = self.recv_skill()

        self.send_skill(msg)

        try:
            # Start connection between the optimizer and the server (UNIX socket)
            with closing(socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM)) as s:
                # define socket options to allow the reuse of the same addr
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Start to listen to the socket
                s.bind((Server.HOST, Server.PORT))
                s.listen(1)

                # Waits for client connection
                self.conn, addr = s.accept()

            with closing(self.conn):
                # Receive socket info from client
                sockname = self.recv_data()['data']

                # Log the connectivity
                log = "Connected to client with address {0}:{1}".format(
                    sockname[0], sockname[1])
                self.send_skill(log)

                data = dict(data=addr)
                self.send_data(data)

                while True:
                    # Receive request from the optimizer
                    req = self.recv_data()

                    # Process the optimizer request
                    expr = self.process_skill_request(req)

                    if expr == 0:
                        break
                    elif expr is None:
                        typ = 'error'
                        obj = "There was an error while processing the sent data"
                    else:
                        # Send the request to Cadence
                        self.send_skill(expr)

                        if expr != 'info':
                            # Wait for the response from Cadence
                            res = self.recv_skill()
                            # Process the Cadence response
                            typ, obj = self.process_skill_response(res)
                            self.count += 1  # Update request number

                            self.send_data(dict(type=typ, data=obj))

        except (OSError, AttributeError, IOError, TypeError, ValueError,
                RuntimeError) as err:
            self.send_warn("Error: {0}".format(err))
        finally:
            self.close()  # Stop the server

    def send_data(self, obj):
        """Send an object using sockets.

        1 - Serialize the object in JSON and enconde the string as a bytes object;
        2 - pack the serialized object length in an unsigned int (I) [four bytes],
            and big-endian byte order (>) (this way the object size message has
            always the same size (four bytes));
        3 - send the data.

        Arguments:
            obj {dict} -- object to send

        Raises:
            TypeError -- if the object is not serializable
            RuntimeError -- if the socket connection is broken
        """
        # Serialize the object in JSON and encode the string as a bytes object
        try:
            serialized = json.dumps(obj).encode()
        except (TypeError, ValueError):
            raise TypeError('It can only send JSON-serializable data')

        serialized_len = len(serialized)  # String length

        # Packed string length
        pack_serialized_len = struct.pack('>I', serialized_len)

        # Data to send
        data = pack_serialized_len + serialized

        total_sent = 0

        while total_sent < serialized_len:
            sent = self.conn.send(data[total_sent:])

            if not sent:
                raise RuntimeError(
                    "Socket connection broken while sending data")

            total_sent += sent

    def recv_data(self):
        """Receive an object using sockets.

        1 - Receive the first four bytes of data, which contains the data lenght;
        2 - Receive the data, serialized in JSON, and decode it;
        3 - Convert the received data in an object.

        Raises:
            RuntimeError -- if the socket connection is broken

        Returns:
            obj {dict} -- decoded and de-serialized received data
        """
        data_len = self.recv_bytes(4)

        if not data_len:
            raise RuntimeError("Socket connection broken while receiving data")

        msg_len = struct.unpack('>I', data_len)[0]

        serialized = self.recv_bytes(msg_len).decode()

        try:
            obj = json.loads(serialized)
        except (TypeError, ValueError):
            raise Exception('Received data is not in JSON format')

        return obj

    def recv_bytes(self, n_bytes):
        """Receive a specified number of bytes using sockets.

        Arguments:
            n_bytes {int} -- number of bytes to receive

        Raises:
            RuntimeError -- if the socket connection is broken

        Returns:
            bytes -- received bytes stream
        """
        data = b''  # Bytes literal
        data_len = len(data)

        while data_len < n_bytes:
            # Receives a maximum of 1024 bytes per iteration
            packet = self.conn.recv(min(n_bytes - data_len, 1024))

            if not packet:
                raise RuntimeError(
                    "Socket connection broken while receiving bytes")

            data_len += len(packet)
            data += packet

        return data

    def send_skill(self, expr):
        """Send a skill expression to Cadence for evaluation.

        Arguments:
            data {str} -- skill expression
        """
        self.server_out.write(expr)
        self.server_out.flush()

    def recv_skill(self):
        """Receive a response from Cadence.

        First receives the message length (number of bytes) and then receives the message.

        Returns:
            str -- message received from cadence
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
            warn {str} -- warning message
        """
        self.server_err.write(warn)
        self.server_err.flush()

    def send_debug(self, msg):
        """Send a debug message to Cadence.

        Arguments:
            msg {str} -- debug message
        """
        time.sleep(1)
        self.send_warn("[Debug] {0}".format(msg))

    def process_skill_request(self, req):
        """Process a skill request from the optimizer.

        Based on the given request object, returns the skill expression to be evaluated by Cadence.

        Arguments:
            req {dict} -- request object

        Returns:
            str|None -- expression to be evaluated by Cadence, if "req" is valid
        """
        try:
            typ = req['type']
            data = req['data']
        except KeyError as err:  # if the key does not exist
            self.send_warn("Error: {0}".format(err))
            return None

        if typ == 'info':
            if data.lower() == 'exit':
                return 0
            return typ
        elif typ == 'loadSimulator':

            self.sim_multi = util.get_parallel_simulations(Server.SIM_FILE)

            return 'loadSimulator( "{0}" "{1}")'.format(
                Server.SIM_FILE, self.sim_multi)
        elif typ == 'updateAndRun':
            # Store circuit variables in file
            vars_file = os.environ.get(
                'PAIM_VAR_PATH') + "/vars{0}.ocn".format(self.count)
            util.store_vars_in_file(data, vars_file)
            # Redefine the path of the simulation results file to be used by cadence
            out_file = os.environ.get(
                'PAIM_RESULT_PATH') + "/out{0}.txt".format(self.count)

            # create empty file
            with open(out_file, 'w'):
                pass

            return 'updateAndRun("{0}" "{1}" "RESULT_FILE={2}" {3})'.format(
                Server.RUN_FILE, vars_file, out_file, len(data))
        else:
            self.send_warn("Invalid object type sent from the client.")
            return None

    def process_skill_response(self, msg):
        """Process the skill response from Cadence.

        Arguments:
            msg {str} -- cadence response

        Returns:
            tuple -- response type (typ) and response object (obj)
        """
        if "loadSimulator_OK" in msg:
            typ = 'loadSimulator'
            vars_path = os.environ.get('PAIM_SCRIPT_PATH') + '/vars.ocn'
            # Get the original circuit variables (user defined) to send
            var = util.get_vars_from_file(vars_path)

            obj = var, self.sim_multi

        elif "updateAndRun_OK" in msg:
            typ = 'updateAndRun'
            # Get the results from file
            out_file = os.environ.get(
                'PAIM_RESULT_PATH') + "/out{0}.txt".format(self.count)
            obj = util.get_results_from_file(out_file)

        else:
            typ = 'info'
            obj = "[INFO from Cadence] {0}".format(msg)

        return typ, obj

    def close(self):
        """Close the server socket."""
        # Send feedback to Cadence
        self.send_warn("Connection with the optimizer ended!\n\n")
        self.server_out.close()  # close stdout
        self.server_err.close()  # close stderr
        self.cad_file.exit(255)  # close connection to cadence (code up to 255)


def start_server():
    """Start the server."""
    server = Server(sys)
    server.run()


if __name__ == "__main__":
    start_server()
