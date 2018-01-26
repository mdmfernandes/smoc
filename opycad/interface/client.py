# -*- coding: utf-8 -*-
"""Client that communicates with Cadence through the server"""

import socket
import struct
import json


class Client(object):
    """A client that handles Cadence requests.

    This client receives data from Cadence (through a server) and processes that data.
    It then gather the results and send them back to Cadence.
    All the data is serialized in JSON and sent as a JSON string.

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

                # Send the local socket name to the server
                self.send_data(
                    dict(type='info', data=self.socket.getsockname()))

                # Receive the remote socket name
                addr = self.recv_data()['data']

                print(
                    f"[INFO] Connected to server with the address {addr[0]}:{addr[1]}")

            except:
                print("Connect Exception")
                self.close()
                raise   # Re-raise this error to call the outter except

        except:
            print("Socket Exception")
            raise       # Re-raise this error to call the except of the main

    def send_data(self, obj):
        """Send an object using sockets

        Arguments:
            obj {dict} -- object to send

        Raises:
            Exception -- if the object is not serializable
            RuntimeError -- if the socket connection is broken
        """
        # Serialize the object in JSON and encode the string as a bytes object
        try:
            serialized = json.dumps(obj).encode()
        except (TypeError, ValueError):
            raise Exception('It can only send JSON-serializable data')

        serialized_len = len(serialized)    # String length

        # Packed string length
        pack_serialized_len = struct.pack('>I', serialized_len)

        # Data to send
        data = pack_serialized_len + serialized

        total_sent = 0

        while total_sent < serialized_len:
            sent = self.socket.send(data[total_sent:])

            if not sent:
                raise RuntimeError("Socket connection broken")

            total_sent += sent

    def recv_data(self):
        """Receive an object using sockets

        Raises:
            RuntimeError -- if the socket connection is broken

        Returns:
            obj {dict} -- decoded and de-serialized received data
        """
        data_len = self.recv_bytes(4)

        if not data_len:
            raise RuntimeError("Socket connection broken")

        # >I means a unsigned int (I) with four bytes length, and big-endian byte order (>)
        msglen = struct.unpack('>I', data_len)[0]

        serialized = self.recv_bytes(msglen).decode()

        try:
            obj = json.loads(serialized)
        except (TypeError, ValueError):
            raise Exception('Received data is not in JSON format')

        return obj

    def recv_bytes(self, n_bytes):
        """Receive a specified number of bytes using sockets

        Arguments:
            n_bytes {integer} -- number of bytes to receive

        Raises:
            RuntimeError -- if the socket connection is broken

        Returns:
            data {bytes} -- received stream of bytes
        """
        data = b''  # Bytes literal
        data_len = len(data)

        while data_len < n_bytes:
            packet = self.socket.recv(min(n_bytes - data_len, 1024))

            if not packet:
                raise RuntimeError("Socket connection broken")

            data_len += len(packet)
            data += packet

        return data

    def close(self):
        """Close the socket"""
        self.socket.close()
