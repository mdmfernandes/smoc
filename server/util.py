# -*- coding: utf-8 -*-
"""This module contains helpers to handle data"""

import re
from functools import reduce


def get_vars_from_file(file_path):
    """Get circuit variables from file and store in a dictionary

    Arguments:
        file_path {string} -- file path

    Returns:
        variables {dict} -- circuit variables
    """
    variables = {}

    # Dictionary with metric prefixes
    prefix_dict = {
        'f': 'e-15',
        'p': 'e-12',
        'n': 'e-9',
        'u': 'e-6',
        'm': 'e-3',
        'k': 'e3',
        'K': 'e3',  # Kilo can be 'k' or 'K' in Cadence
        'M': 'e6',
        'G': 'e9',
        'T': 'e12'
    }

    pattern = r'desVar\(\s*\"(?P<param>\w+)\"\s*(?P<value>\S+)\s*\)'

    with open(file_path, 'r') as f:
        content = f.read()

    for match in re.finditer(pattern, content):
        try:    # try to convert value to float
            value = float(match.group('value'))
        except ValueError:
            # If fails, replace the prefixes by the respective exponents
            value = float(reduce((lambda a, kv: a.replace(*kv)),
                                 prefix_dict.items(), match.group('value')))

        # Save to dict
        variables[match.group('param')] = value

    return variables


def store_vars_in_file(variables, file_path):
    """Store circuit variables in a file

    Arguments:
        var {dict} -- dictionary with the circuit variables
        file_path {string} -- file path
    """

    with open(file_path, 'w') as f:

        for idx, var in enumerate(variables):
            # Write the header of the correspondent test
            f.write("ocnxlSelectTest(\"test:{0}\")\n".format(idx+1))

            # Iterate over the dictionary and save variables to file
            for key, val in var.items():
                f.write("desVar(\t \"{0}\" {1}\t)\n".format(key, val))


def get_results_from_file(file_path):
    """Get simulation results from file and store in a dictionary

    Arguments:
        file_path {string} -- file path
        n_sims {int} -- number of simulations runing in parallel

    Returns:
        results_list {list} -- simulation results in a list of dictionaries
    """
    results = {}

    pattern = r'\s*(?P<param>\S+)\s+(?P<value>\S+)'

    with open(file_path, 'r') as f:
        content = f.read()

    results_list = []

    for match in re.finditer(pattern, content):
        key = match.group('param')
        val = float(match.group('value'))

        if key in results:
            results_list.append(results)
            results = {}

        results[key] = val  # Save to dict

    results_list.append(results)    # Append the last dict

    return results_list
