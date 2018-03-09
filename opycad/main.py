#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimizer root module"""

import sys

import matplotlib.pyplot as plt

from interface.client import Client
from interface.menu import print_menu
from util.file import read_yaml


def start_simulator():
    pass


def update_and_run():
    pass


def process_server_response(res):
    try:
        typ = res['type']
        data = res['data']
    except KeyError as err:  # if the key does not exist
        print(f"Error: {err}")
        return None

    # If response type is loadSimulator we want to receive the original (user defined)
    # circuit variables... to start to optimize from somewhere
    if 'loadSimulator' in typ:
        for key, val in data.items():
            print(f"Key: {key} - Val:{val}")

        return 'vars', data
    # If response type is updateAndRun we want to receive simulation results to
    # fed into the optimizer
    elif 'updateAndRun' in typ:
        print('Recebeu updateAndRun')

        print(data)
        '''plt.plot(range(len(data)), data.values())
        plt.draw()
        plt.pause(2) '''

        return 'results', data
    else:
        # Não devia vir aqui
        print("Não devia vir aqui")
        return None, None


def main():
    """Optimizer main function."""
    plt.ion()
    plt.show()

    # Load server host, port
    server = read_yaml()['server']
    host = server['host']
    port = server['port']

    # Start the client
    try:
        print("Connecting to server...")
        client = Client(host, port)
    except RuntimeError as err:
        print("[ClientError] {0}".format(err))
        return 0

    data = {}
    variables = {}  # Circuit variables (to be optimized)
    results = {}    # Simulation results (to fed the optimizer)

    # Program loop
    while True:
        try:
            option = print_menu()

            if not option:  # if option == 0
                print("Shutting down.")
                req = dict(type='info', data='exit')
                client.send_data(req)
                break
            elif option == 1:
                req = dict(type='loadSimulator', data='ola')
            elif option == 2:
                print("Sending updated variables...")
                for key, val in variables.items():
                    print(f"Key: {key} - Val:{val}")
                req = dict(type='updateAndRun', data=variables)
            else:
                raise RuntimeError("Nunca devia ter chegado aqui!!!")

            client.send_data(req)

            #
            # Wait for data from server
            #
            res = client.recv_data()

            typ, data = process_server_response(res)

            if typ == 'vars':
                variables = data
            elif typ == 'results':
                # results = data
                for key, val in variables.items():
                    variables[key] = val + val * 0.1
            else:
                print("Server response: Não devia ter vindo aqui")

        except:
            print(f"my Error: {sys.exc_info()}")
            raise

    client.close()  # Close the socket
    print("--- END OF CLIENT ---")


if __name__ == "__main__":
    main()
    