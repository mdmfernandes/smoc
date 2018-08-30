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
    objectives = {'POWER': [-1.0, 'W'], 'GAIN': [1.0, 'dB']}

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
        'W1':    [(1,   100), 'um'],
        'W2':    [(3,   100), 'um'],
        'L':     [(140e-3, 4*140e-3), 'um'],
        'IB':    [(10e-6,  100e-6), 'A'],
        'VBIAS': [(0.3,    1.0), 'V']
    }

    return objectives, constraints, circuit_vars


def main():
    """Optimizer main function."""

    # Load server host, port
    server = read_yaml()['server']
    host = server['host']
    port = server['port']

    debug = True

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

        print(f"Circuit Variables: {list(circuit_vars.keys())}")

        # Optimizer parameters (TODO: get from somewhere)
        pop_size = 20
        max_gen = 2
        sim_multi = 8   # Number of parallel simulations

        # Remove the units from the "circuit_vars" and from the "objectives"
        circuit_vars_tmp = {key: val[0] for key, val in circuit_vars.items()}
        objectives_tmp = {key: val[0] for key, val in objectives.items()}

        # Load the optimizer
        paim = OptimizerNSGA2(objectives_tmp, constraints, circuit_vars_tmp, pop_size,
                              max_gen, sim_multi, client=client, debug=debug)


        # Define the checkpoint and logbook file names
        current_time = time.strftime("%Y%m%d_%H-%M", time.localtime())
        checkpoint_fname = f"/home/miguel/Drive/dev/paim/logs/checkpoint/cp_{current_time}.pickle"

        checkpoint = "/home/miguel/Drive/dev/paim/logs/checkpoint/cp_20180830_21-39.pickle"

        # Run the GA
        fronts, logbook = paim.run_ga(checkpoint_fname, checkpoint=checkpoint)

        # Save logbook pickled to file
        with open(f"../logs/logbook/logbook{current_time}.pickle", 'wb') as f:
            pickle.dump(logbook, f)

        # Print statistics
        plt.plot_pareto_fronts(fronts, circuit_vars, objectives, plot_file='fronts.html')

        # plt.plot_pareto_fronts_animated(logbook, toolbox.evaluate, tools.emo.sortLogNondominated)

        print("\nShutting down.")
        req = dict(type='info', data='exit')
        client.send_data(req)

    except:
        print(f"my Error: {sys.exc_info()}")
        raise

    client.close()  # Close the socket
    print("--- END OF CLIENT ---")

    return None


if __name__ == "__main__":
    main()
