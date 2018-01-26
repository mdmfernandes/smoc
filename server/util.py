# -*- coding: utf-8 -*-
"""This module contains util functions to handle data"""

import re
from functools import reduce


def get_vars_from_file(file_path):
    """Get the circuit variables from file and store them in a dictionary

    Arguments:
        file_path {string} -- file path

    Returns:
        variables {dictionary} -- circuit variables
    """
    variables = {}

    # Dictionary with metric prefixs
    prefix_dict = {
        'f': 'e-15',
        'p': 'e-12',
        'n': 'e-9',
        'u': 'e-6',
        'm': 'e-3',
        'k': 'e3',
        'M': 'e6',
        'G': 'e9',
        'T': 'e12'
    }

    pattern = r'^desVar\(\s*\"(\w+)\"\s*(\S+)\s*\)$'

    with open(file_path, 'r') as f:
        for line in f:
            match = re.findall(pattern, line)

            key = match[0][0]
            val = match[0][1]

            # try to convert val to float
            try:
                val = float(val)
            except ValueError:
                # If it's not possible, replace the prefixs by the respective exponentials
                val = reduce((lambda a, kv: a.replace(*kv)),
                             prefix_dict.items(), val)

            variables[key] = float(val)

    return variables


def store_vars_in_file(variables, file_path):
    """Store the circuit variables in a file

    Arguments:
        var {dict} -- dictionary with the circuit variables
        file_path {string} -- file path
    """
    with open(file_path, 'w') as f:
        # Iterate over the dictionary and save to file
        for key, val in variables.items():
            f.write(f"desVar(\t \"{key}\" {val}\t)\n")
