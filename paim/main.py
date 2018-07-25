#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Optimizer root module"""

import sys

from interface.client import Client
from interface.menu import print_menu
from util.file import read_yaml
from optimizer.ga import OptimizerNSGA2

from util import plot as plt

import pickle

import time


def load_simulator(client):
    """[summary]

    Arguments:
        client {[type]} -- [description]

    Raises:
        Exception -- [description]

    Returns:
        [type] -- [description]
    """

    req = dict(type='loadSimulator', data=None)
    client.send_data(req)
    res = client.recv_data()

    try:
        res_type = res['type']
        data = res['data']
    except KeyError as err:  # if the key does not exist
        print(f"Error: {err}")

    if res_type != 'loadSimulator':
        raise Exception('The response type should be "loadSimulator"!!!')

    return data


def get_circuit_params_from_file():
    """[summary]

    Returns:
        [type] -- [description]
    """
    # TODO: Read from somewhere...
    # Define cicuit parameters
    objectives = {'POWER': -1.0, 'GAIN': 1.0}

    constraints = {  # 'VDSAT':     (50e-3, 1.0),
        # 'VDS_VDSAT': (50e-3, 1.2),
        'GBW':       (10e6,  1e9),
        'GAIN':      (30,    100),
        'OS':        (0.7,   1.2),
        # 0: off, 1: triode, 2: sat, 3: subth, 4: breakdown
        'REG1':      2,
        'REG2':      2
    }

    # Genes de um individuo - W1, W2 (=WB), L (=L1=L2=LB), Ib, Vbias(=VGS1)
    circuit_vars = {
        'W1':    (1,   100),
        'W2':    (3,   100),
        'L':     (140e-3, 4*140e-3),
        'IB':    (10e-6,  100e-6),
        'VBIAS': (0.3,    1.0)
    }

    return objectives, constraints, circuit_vars


def main():
    """Optimizer main function."""

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

    objectives, constraints, circuit_vars = get_circuit_params_from_file()

    try:
        print("[INFO] Loading simulator...")
        res_vars = load_simulator(client)

        diff = set(circuit_vars.keys()) - set(res_vars.keys())

        if diff:    # If it's not empty (i.e. bool(diff) is True)
            raise Exception(
                "The circuit variables don't mach with the variables provided in the file")

        print(f"Circuit Variables: {circuit_vars.keys()}")

        # Optimizer parameters (TODO: get from somewhere)
        pop_size = 10
        max_gen = 5

        # Load the optimizer
        paim = OptimizerNSGA2(objectives, constraints, circuit_vars, pop_size,
                              max_gen, client=client)

        fronts, logbook = paim.run_ga(stats=True, verbose=True)

        current_time = time.strftime("%Y%m%d_%H-%M", time.localtime())
        # Save logbook pickled to file
        with open(f"../logs/logbook{current_time}.pickle", 'wb') as f:
        # Iterate over the dictionary and save to file
            pickle.dump(logbook, f)

        # Save fronts (pop of the last run) pickled to file
        with open(f"../logs/fronts{current_time}.pickle", 'wb') as f:
        # Iterate over the dictionary and save to file
            pickle.dump(fronts, f)

        # Read do logbook só para confirmar
        # with open(f"../logs/logbook{current_time}.pickle", 'rb') as f:
        #     oi = pickle.load(f)

        # print(oi)

        # Print statistics
        plt.plot_pareto_fronts(fronts, paim.toolbox.evaluate)

        # plt.plot_pareto_fronts_animated(logbook, toolbox.evaluate, tools.emo.sortLogNondominated)

        input("Press any key to close the program...")
        
        print("Shutting down.")
        req = dict(type='info', data='exit')
        client.send_data(req)

    except:
        print(f"my Error: {sys.exc_info()}")
        raise

    client.close()  # Close the socket
    print("--- END OF CLIENT ---")


if __name__ == "__main__":
    main()
