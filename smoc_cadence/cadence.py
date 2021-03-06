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
"""This module handles the communication between Cadence and the server."""

import os
import sys

import util

# Try to import 'Server' from the global package 'socad'
try:
    from socad import Server
except ImportError as err:
    # If can't import from the global package
    try:  # Try to import from interface.server
        from interface.server import Server
    except ImportError as err:
        # If can't import the package, quit the program
        print("[ERROR] {0}. Exiting...".format(err))
        sys.exit('1')

# Simulator files
SIM_FILE = os.environ.get('SMOC_LOAD_FILE')
SET_SIM_FILE = os.environ.get('SMOC_SET_SIM_FILE')
TEMPLATE_FILE = os.environ.get('SMOC_TEMPLATE_FILE')
RUN_FILE = os.environ.get('SMOC_RUN_FILE')
VAR_FILE = os.environ.get('SMOC_VARS_FILE')
ROOT_DIR = os.environ.get('SMOC_ROOT_DIR')
OUT_FILE = os.environ.get('SMOC_RESULTS_FILE')
# Client config
HOST = os.environ.get('SMOC_CLIENT_ADDR')
PORT = int(os.environ.get('SMOC_CLIENT_PORT'))


def process_skill_request(req):
    """Process a skill request from the optimizer.

    Based on the given request object, returns the skill expression to be
    evaluated by Cadence.

    Arguments:
        req (dict): request object.

    Raises:
        KeyError: if the input request format is invalid.
        TypeError: if the type parameter of the received object is invalid.

    Returns:
        str: expression to be evaluated by Cadence.
    """
    try:
        type_ = req['type']
        data = req['data']
    except KeyError as err:  # if the key does not exist
        raise KeyError(err)

    if type_ == 'info' and data.lower() == 'exit':
        res = 'exit'

    elif type_ == 'loadSimulator':
        pop_size = data
        util.generate_simulations_file(TEMPLATE_FILE, SET_SIM_FILE, pop_size)
        res = 'loadSimulator("{0}" "{1}" "{2}")'.format(ROOT_DIR, SIM_FILE, pop_size)

    elif type_ == 'updateAndRun':
        # Store circuit variables in file
        util.store_vars_in_file(data, VAR_FILE)
        res = 'updateAndRun("{0}" "{1}" "SMOC_RESULTS_FILE={2}" {3})'.format(
            RUN_FILE, VAR_FILE, OUT_FILE, len(data))
    else:
        raise TypeError("Invalid object received from the client.")

    return res


def process_skill_response(msg):
    """Process the skill response from Cadence.

    Arguments:
        msg (str): cadence response.

    Raises:
        TypeError: if the input message format is invalid.

    Returns:
        tuple: response type (type_) and response object (obj).
    """
    if "loadSimulator_OK" in msg:
        type_ = 'loadSimulator'
        # Get the original circuit variables (user defined) to send
        var = util.get_vars_from_file(VAR_FILE)

        obj = var

    elif "updateAndRun_OK" in msg:
        type_ = 'updateAndRun'
        # Get the results from file
        obj = util.get_results_from_file(OUT_FILE)

    else:
        raise TypeError("Invalid message received from Cadence.")

    return type_, obj


def main():
    """Module main function."""
    try:
        # Start the server
        server = Server(sys)
    except OSError as err:
        server.send_warn("[SOCKET ERROR] {0}".format(err))
        return 1

    try:
        addr = server.run(HOST, PORT)

        # Log the connectivity to Cadence
        log = "Connected to client with address {0}:{1}".format(addr[0], addr[1])
        server.send_skill(log)

    except IOError as err:  # NOTE: "ConnectionError" don't exist in Python 2 -_-
        server.send_warn("[CONNECTION ERROR] {0}".format(err))
        return 1

    code = 0  # Return code
    try:
        while True:
            # Wait for a client request
            req = server.recv_data()

            # Process the client request
            expr = process_skill_request(req)

            if expr == 'exit':
                break
            else:
                # Send the request to Cadence
                server.send_skill(expr)
                # Wait for a response from Cadence
                res = server.recv_skill()
                # Process the Cadence response
                typ, obj = process_skill_response(res)
                # Send the processed response to the client
                server.send_data(dict(type=typ, data=obj))

    except IOError as err:  # NOTE: "ConnectionError" don't exist in Python 2 -_-
        server.send_warn("[CONNECTION ERROR] {0}".format(err))
        code = 2
    except TypeError as err:
        server.send_warn("[TYPE ERROR] {0}".format(err))
        code = 3
    except KeyError as err:
        server.send_warn("[KEY ERROR] {0}".format(err))
        code = 4

    server.close(code)
    return code


if __name__ == "__main__":
    sys.exit(main())
