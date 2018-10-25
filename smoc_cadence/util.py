# This file is part of SMOC
# Copyright (C) 2018  Miguel Fernandes
#
# SMOC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SMOC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Helpers to handle data."""

import re
from functools import reduce


def get_vars_from_file(fname):
    """Get circuit variables from file and store in a dictionary.

    Arguments:
        fname (str): file path.

    Returns:
        dict: circuit variables.
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

    with open(fname, 'r') as f:
        content = f.read()

    for match in re.finditer(pattern, content):
        try:  # try to convert value to float
            value = float(match.group('value'))
        except ValueError:
            # If fails, replace the prefixes by the respective exponents
            value = float(reduce((lambda a, kv: a.replace(*kv)), prefix_dict.items(),
                                 match.group('value')))

        # Save to dict
        variables[match.group('param')] = value

    return variables


def store_vars_in_file(variables, fname):
    """Store circuit variables in a file.

    Arguments:
        variables (dict): dictionary with the circuit variables.
        fname (str): file name.
    """
    with open(fname, 'w') as f:

        for idx, var in enumerate(variables):
            # Write the header of the correspondent test
            f.write("ocnxlSelectTest(\"test:{0}\")\n".format(idx + 1))

            # Iterate over the dictionary and save variables to file
            for key, val in var.items():
                f.write("desVar(\t \"{0}\" {1}\t)\n".format(key, val))


def get_results_from_file(fname):
    """Get simulation results from file and store in a dictionary.

    Arguments:
        fname (str): file path.
        n_sims (int): number of simulations runing in parallel.

    Returns:
        list: simulation results in a list of dictionaries.
    """
    results = {}

    pattern = r'\s*(?P<param>\S+)\s+(?P<value>\S+)'

    with open(fname, 'r') as f:
        content = f.read()

    results_list = []

    for match in re.finditer(pattern, content):
        key = match.group('param')
        val = float(match.group('value'))

        if key in results:
            results_list.append(results)
            results = {}

        results[key] = val  # Save to dict

    results_list.append(results)  # Append the last dict

    return results_list


def generate_simulations_file(template, fname, pop_size):
    # Read the template
    with open(template, 'r') as f:
        content = f.read()

    # Write the simulations file
    with open(fname, 'w') as f:
        for idx in range(1, pop_size + 1):
            f.write('ocnxlBeginTest("test:{0}")\n'.format(idx))
            f.write(content)
            f.write("ocnxlEndTest()\n\n")
