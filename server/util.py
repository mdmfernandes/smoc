# -*- coding: utf-8 -*-
"""This module contains util functions to handle data"""

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

    pattern = r'desVar\(\s*"(?P<param>\w+)\"\s*(?P<value>\S+)\s*\)'

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
        # Iterate over the dictionary and save to file
        for key, val in variables.items():
            f.write(f"desVar(\t \"{key}\" {val}\t)\n")


def get_results_from_file(file_path):
    """Get simulation results from file and store in a dictionary

    Arguments:
        file_path {string} -- file path

    Returns:
        results {dict} -- simulation results
    """
    results = {}

    pattern = r'\s*(?P<param>\S+)\s+(?P<value>\S+)'

    with open(file_path, 'r') as f:
        content = f.read()

    for match in re.finditer(pattern, content):
        # Save to dict
        results[match.group('param')] = float(match.group('value'))

    return results
