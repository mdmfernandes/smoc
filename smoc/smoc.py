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
"""SMOC main module."""

import logging
import os
import time

from socad import Client
from .optimizer.ga import OptimizerNSGA2
from .util import file
from .util import plot as plt


def load_simulator(client, pop_size):
    """Load the Cadence simulator before starting the optimization.

    This task is performed once per run (contrary to the Cadence ADE) that
    loads the simulator everytime we run a simulation, which is very
    inefficient.

    Arguments:
        client (handler): client that communicates with the simulator.
        pop_size (int): population size.

    Raises:
        KeyError: if the response format is invalid.
        TypeError: if the server response is not from the expected type.

    Returns:
        dict: circuit design variables.
    """
    req = dict(type='loadSimulator', data=pop_size)
    client.send_data(req)
    res = client.recv_data()

    try:
        res_type = res['type']
        data = res['data']
    except KeyError as err:  # if the key does not exist
        raise KeyError(err)

    if res_type != 'loadSimulator':
        raise TypeError('The response type should be "loadSimulator"!!!')

    return data


def print_summary(log_file, current_time, project_cfg, optimizer_cfg, server_cfg,
                  objectives, constraints, circuit_vars, checkpoint_load, debug):
    """Print a summary with the project, circuit, and optimizer configurations.

    Arguments:
        log_file (str): file where to print the summary.
        current_time (str): current date and time.
        project_cfg (dict): project configuration parameters.
        optimizer_cfg (dict): optimizer configuration parameters.
        server_cfg (dict): server configuration parameters.
        objectives (dict): optimization objectives.
        constraints (dict): optimization constraints.
        circuit_vars (dict): circuit design variables.
        checkpoint_load (str or None): checkpoint file to load, if provided.
        debug (bool): running mode (debug mode if True).
    """
    running_mode = "debug" if debug else "normal"
    checkpoint_fname = checkpoint_load.split('/')[-1].split('.')[0] if checkpoint_load else "no"

    summary = f"""
********************************************************************************
****** SMOC - A Stochastic Multi-objective Optimizer for Cadence Virtuoso ******
********************************************************************************
* Running date and time: {current_time}              
* Project name: {project_cfg['project_name']}            
* Project path: {project_cfg['project_path']}        
* Running mode (normal/debug): {running_mode}        
* Running from checkpoint: {checkpoint_fname}        
***************************** Optimizer parameters *****************************
* Population size: {optimizer_cfg['pop_size']}
* # of individuals to select: {optimizer_cfg['mu']}
* # of children to produce: {optimizer_cfg['lambda']}
* # of generations: {optimizer_cfg['max_gen']}
* Mutation probability: {optimizer_cfg['mut_prob']}
* Crossover probability: {optimizer_cfg['cx_prob']}
* Mutation crowding degree: {optimizer_cfg['mut_eta']}
* Crossover crowding degree: {optimizer_cfg['cx_eta']}
* Fitness penalty delta: {optimizer_cfg['penalty_delta']}
* Fitness penalty weight: {optimizer_cfg['penalty_weight']}
**************************** Optimization objectives ***************************\n"""
    for key, val in objectives.items():
        summary += f"* {key}: {val[0]} [{val[1]}]\n"
    summary += "*************************** Optimization constraints ***************************\n"
    for key, val in constraints.items():
        summary += f"* {key}: min = {val[0][0]}, max = {val[0][1]} [{val[1]}]\n"
    summary += "*************************** Circuit design variables ***************************\n"
    for key, val in circuit_vars.items():
        summary += f"* {key}: min = {val[0][0]}, max = {val[0][1]} [{val[1]}]\n"
    summary += "******************************* Server parameters ******************************\n"
    summary += f"* Host: {server_cfg['host']}\n"
    summary += f"* Port: {server_cfg['port']}\n"
    summary += "********************************************************************************\n"

    print(summary)

    with open(log_file, 'a') as f:
        f.write(summary)


def create_logger(verbose, fname):
    """Create a logger to print to console and file the program logs

    The verbosity affects the messages type that are logged to file. All messages
    are always logged to the console.
    Verbose:
        - 0: No messages
        - 1: Only Error and Critical messages.
        - 2+: Info, Warning, Error, and Critical messages.

    Args:
        verbose (int): program verbosity.

    Returns:
        logger: logger object.
    """
    # Create a custom logger
    logger = logging.getLogger('smoc')
    # The logger level should be equal or higher than the handlers level
    logger.setLevel(logging.INFO)

    # Create file handler if verbose > 0
    if verbose > 0:
        f_handler = logging.FileHandler(fname)
        # Select handler level
        if verbose == 1:
            f_handler.setLevel(logging.ERROR) # Error, Critical
        else:
            f_handler.setLevel(logging.INFO) # Info, Warning, Error, Critical

        # Format file handler
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                     datefmt='%Y-%m-%d %H:%M:%S')
        f_handler.setFormatter(f_format)
        # Add the file handler to the logger
        logger.addHandler(f_handler)


    # Create console handler
    c_handler = logging.StreamHandler()
    # Create formatters and add it to handlers
    c_format = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', datefmt='%H:%M:%S')
    c_handler.setFormatter(c_format)
    c_handler.setLevel(logging.INFO) # Info, Warning, Error, Critical
    # Add the handler to the logger
    logger.addHandler(c_handler)

    return logger


def run_smoc(config_file, checkpoint_load, debug):
    """Run SMOC.

    Arguments:
        config_file (str): path of configuration file.
        checkpoint_load (str or None): checkpoint file to load, if provided.
        debug (boolean): running mode (debug mode if True).

    Raises:
        ValueError: if the circuit variables don't match with the variables
                    provided in the configuration file.

    Returns:
        int: exit code.
    """
    # Read config file and load the configurations into variables
    smoc_cfg = file.read_yaml(config_file)

    if not smoc_cfg:  # If config is not valid
        print("[ERROR] Invalid config file...")
        print("\n**** Ending program... Bye! ****")
        return 1

    # Get the configs
    project_cfg = smoc_cfg['project_cfg']
    optimizer_cfg = smoc_cfg['optimizer_cfg']
    objectives = smoc_cfg['objectives']
    constraints = smoc_cfg['constraints']
    server_cfg = smoc_cfg['server_cfg']

    # Get current date and time
    current_time = time.strftime("%Y%m%d_%H-%M", time.localtime())

    # Define the checkpoint/logbook/plot file names
    project_dir = f"{project_cfg['project_path']}/{project_cfg['project_name']}"
    checkpoint_dir = project_dir + f"/{project_cfg['checkpoint_path']}"
    checkpoint_fname = checkpoint_dir + f"/cp_{current_time}.pickle"
    logbook_dir = project_dir + f"/{project_cfg['logbook_path']}"
    logbook_fname = logbook_dir + f"/lb_{current_time}.pickle"
    plot_dir = project_dir + f"/{project_cfg['plot_path']}"
    plot_fname = plot_dir + f"/plt_{current_time}.html"

    # Get the verbosity
    verbose = project_cfg['verbose']

    # The file where to print the logs
    log_file = f"{project_dir}/{current_time}.log"

    logger = create_logger(verbose, log_file)

    try:
        logger.info("Starting client...")
        client = Client()
    except OSError as err:
        logger.error("SOCKET - %s", err)
        print("\n**** Ending program... Bye! ****")
        return 2

    return_code = 0

    try:
        logger.info("Connecting to server...")
        addr = client.run(server_cfg['host'], server_cfg['port'])
        logger.info("Connected to server with the address %s:%s", addr[0], addr[1])

        # Get the population size
        pop_size = optimizer_cfg['pop_size']

        # Check if "mu" and "lambda" are defined in the config file.
        # If not, theirvalue is equal to the "pop_size"
        if not 'mu' in optimizer_cfg:
            optimizer_cfg['mu'] = pop_size
        if not 'lambda' in optimizer_cfg:
            optimizer_cfg['lambda'] = pop_size

        # Load the simulator
        logger.info("Loading simulator...")
        res_vars = load_simulator(client, pop_size)

        circuit_vars = smoc_cfg['circuit_vars']
        diff = set(circuit_vars.keys()) - set(res_vars.keys())

        if diff:  # If it's not empty (i.e. bool(diff) is True)
            err = "The circuit variables don't match with the variables provided in the file"
            raise ValueError(err)

        # Create the required directories, if they do not exist
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        if not os.path.exists(logbook_dir):
            os.makedirs(logbook_dir)
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)

        # Print the configurations summary
        print_summary(log_file, current_time, project_cfg, optimizer_cfg, server_cfg,
                      objectives, constraints, circuit_vars, checkpoint_load, debug)

        # Remove the units from the "circuit_vars", "objectives" and "constraints"
        circuit_vars_tmp = {key: val[0] for key, val in circuit_vars.items()}
        objectives_tmp = {key: val[0] for key, val in objectives.items()}
        constraints_tmp = {key: val[0] for key, val in constraints.items()}

        # Load the optimizer
        smoc_ga = OptimizerNSGA2(objectives_tmp, constraints_tmp, circuit_vars_tmp,
                                 pop_size, optimizer_cfg['max_gen'], client,
                                 optimizer_cfg['mut_prob'], optimizer_cfg['cx_prob'],
                                 optimizer_cfg['mut_eta'], optimizer_cfg['cx_eta'],
                                 optimizer_cfg['penalty_delta'], optimizer_cfg['penalty_weight'],
                                 debug)

        # Run the GA
        fronts, logbook = smoc_ga.run_ga(checkpoint_fname,
                                         optimizer_cfg['mu'],
                                         optimizer_cfg['lambda'],
                                         checkpoint_load,
                                         optimizer_cfg['checkpoint_freq'],
                                         optimizer_cfg['sel_best'],
                                         verbose)

        # End the connection with the server
        logger.info("Ending connection with the server...")
        req = dict(type='info', data='exit')
        client.send_data(req)
        client.close()  # Close the client socket

        # Save logbook pickled to file
        file.write_pickle(logbook_fname, logbook)

        # Print statistics
        logger.info("Plotting the pareto fronts...")
        plt.plot_pareto_fronts(fronts, circuit_vars, objectives, constraints, plot_fname=plot_fname)

    except ConnectionError as err:
        logger.error("CONNECTION - %s", err)
        return_code = 3
    except (TypeError, ValueError) as err:
        logger.error("TYPE/VALUE ERROR - %s", err)
        return_code = 4
    except KeyError as err:
        logger.error("KEY ERROR - %s", err)
        return_code = 5

    # If there was an exception (return_code != 0) it's necessary to close the socket
    if return_code:
        client.close()

    print("\n**** Closing socket and ending program... Bye! ****")
    return return_code
