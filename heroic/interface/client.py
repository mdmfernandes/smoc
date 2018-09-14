# This file is part of HEROiC
# Copyright (C) 2018 Miguel Fernandes
#
# HEROiC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HEROiC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Client that communicates with Cadence through the server."""

import json
import socket
import struct


class Client:
    """A client that handles Cadence requests.

    This client receives data from Cadence (through a server) and processes that data.
    It then gather the results and send them back to Cadence.
    All the data is serialized in JSON and sent as a JSON string.

    Keyword Arguments:
        sock {obj} -- socket to use in the connection (default: None)
    """

    def __init__(self, sock=None):
        """Create the client socket."""
        if sock is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = sock

    def run(self, host, port):
        """Start the client.

        Arguments:
            host {str} -- remote socket IP address
            port {int} -- remote socket port

        Raises:
            ConnectionError -- if can't connect to server

        Returns:
            list -- remote socket name
        """
        try:
            # Try to connect to the specified server
            self.socket.connect((host, port))
        except OSError as err:
            raise ConnectionError(err)

        # Send the local socket name to the server
        self.send_data(dict(type="info", data=self.socket.getsockname()))

        # Receive the remote socket name
        return self.recv_data()["data"]

    def send_data(self, obj):
        """Send an object through a socket.

        1 - Serialize the object in JSON and enconde the string as a bytes object;
        2 - pack the serialized object length in an unsigned int (I) [four bytes],
            and big-endian byte order (>) (this way the object size message has
            always the same size (four bytes));
        3 - send the data.

        Arguments:
            obj {dict} -- object to send

        Raises:
            TypeError -- if the object is not serializable in JSON
            ConnectionError -- if the socket connection is broken
        """
        # Serialize the object in JSON and encode the string as a bytes object
        try:
            serialized = json.dumps(obj).encode()
        except (TypeError, ValueError):
            raise TypeError("It can only send JSON-serializable data")

        serialized_len = len(serialized)  # String length

        # Packed string length
        pack_serialized_len = struct.pack(">I", serialized_len)

        # Data to send
        data = pack_serialized_len + serialized

        total_sent = 0

        while total_sent < serialized_len:
            sent = self.socket.send(data[total_sent:])

            if not sent:
                raise ConnectionError("Socket connection broken while sending data")

            total_sent += sent

    def recv_data(self):
        """Receive an object through a socket.

        1 - Receive the first four bytes of data, which contains the data lenght;
        2 - Receive the data, serialized in JSON, and decode it;
        3 - Convert the received data in an object.

        Raises:
            ConnectionError -- if the socket connection is broken
            TypeError -- if the received data is not in JSON format

        Returns:
            dict -- decoded and de-serialized received data
        """
        data_len = self.recv_bytes(4)

        if not data_len:
            raise ConnectionError("Socket connection broken while receiving data")

        # >I means a unsigned int (I) (with four bytes length) and big-endian byte order (>)
        msglen = struct.unpack(">I", data_len)[0]

        serialized = self.recv_bytes(msglen).decode()

        try:
            obj = json.loads(serialized)
        except (TypeError, ValueError):
            raise TypeError("Received data is not in JSON format")

        return obj

    def recv_bytes(self, n_bytes):
        """Receive a specified number of bytes through a socket.

        Arguments:
            n_bytes {int} -- number of bytes to receive

        Raises:
            ConnectionError -- if the socket connection is broken

        Returns:
            bytes -- received stream of bytes
        """
        data = b""  # Bytes literal
        data_len = len(data)

        while data_len < n_bytes:
            packet = self.socket.recv(min(n_bytes - data_len, 1024))

            if not packet:
                raise ConnectionError("Socket connection broken while receiving a byte")

            data_len += len(packet)
            data += packet

        return data

    def close(self):
        """Close the socket."""
        self.socket.close()