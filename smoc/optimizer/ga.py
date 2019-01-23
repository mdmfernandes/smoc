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
"""NSGA-II genetic algorithm using DEAP."""

import array
import copy
import logging
import math
import random
import time

from deap import algorithms, base, creator, tools

from ..util import file

logger = logging.getLogger('smoc.ga')

# Organize everything in the class
class OptimizerNSGA2:
    """A simulation-based circuit optimizer based on the NSGA-II algorithm.

    This optimizer is based on DEAP and requires connection to a circuit
    simulation environment (e.g. Cadence Virtuoso). It was designed to be
    circuit and simulator independent, requiring only the optimization
    objectives and constraints, and the circuit variables.
    After finishing the optimization, it returns the optimal pareto front
    and the logbook.

    DEAP source: https://deap.readthedocs.io/en/master/

    Arguments:
        objectives (dict): optimization objectives (fitness).
        constraints (dict): optimization constraints (circuit requirements).
        circuit_vars (dict): circuit design variables.
        pop_size (int): population size.
        max_gen (int): max generations.
        client (handler, optional): client that communicates with the simulator
            (default: None).
        mut_prob (float, optional): probability of mutation (default: 0.1).
        cx_prob (float, optional): probability of crossover (default: 0.8).
        mut_eta (int, optional): crowding degree of the mutation (default: 20).
        cx_eta (int, optional): crowding degree of the crossover (default: 20).
        penalty_delta (float, optional): constant value of penalization for an
            invalid individual (default: 2).
        penalty_weight (float, optional): multiplication factor of an invalid
            individual penalty. Changes the variation rate of the fitness
            penalty with the distance from a valid value (default: 1).
        debug (bool, optional): debug (default: False).
    """

    # pylint: disable=too-many-instance-attributes,no-member
    def __init__(self, objectives, constraints, circuit_vars, pop_size, max_gen,
                 client=None, mut_prob=0.1, cx_prob=0.8, mut_eta=20, cx_eta=20,
                 penalty_delta=2, penalty_weight=1, debug=False):
        """Create the NSGA-II Optimizer using the DEAP library."""
        # If debugging we should have a fixed seed to have coherent results
        if debug:
            random.seed(16384)

        # INFO: The sum of mut_prob and cx_prob shall be in [0, 1]
        self.mut_prob = mut_prob
        self.cx_prob = cx_prob
        self.objectives = objectives
        self.constraints = constraints
        self.circuit_vars = list(circuit_vars.keys())
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.penalty_delta = penalty_delta
        self.penalty_weight = penalty_weight

        if client is not None:
            self.client = client

        # Set bounds
        bound_low = []
        bound_up = []
        # Get the bounds from the circuit_vars
        for val in circuit_vars.values():
            bound_low.append(float(val[0]))
            bound_up.append(float(val[1]))

        # Define the Fitness
        fitness_weights = tuple(objectives.values())
        creator.create("FitnessMulti", base.Fitness, weights=fitness_weights)
        # Define an individual
        creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMulti,
                       result=dict)

        toolbox = base.Toolbox()

        # random generated float
        toolbox.register("attr_float", self.uniform, bound_low, bound_up)
        # Define an individual as a list of floats (iterate over "att_float"
        # and place the result in "creator.Individual")
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_float)
        # Define the population as a list of individuals (the # of individuals
        # is only defined when the population is initialized)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # operator for selecting individuals for breeding the next generation
        toolbox.register("select", tools.selNSGA2)

        # register the goal / fitness function
        toolbox.register("evaluate", self.eval_circuit)
        # The constraints handling is made in the "eval_circuit" function
        ##self.toolbox.decorate("evaluate", (self.feasibility, 0, self.distance))

        # register the crossover operator
        toolbox.register("mate", tools.cxSimulatedBinaryBounded,
                         low=bound_low, up=bound_up, eta=cx_eta)

        # register the mutation operator
        toolbox.register("mutate", tools.mutPolynomialBounded, low=bound_low,
                         up=bound_up, eta=mut_eta, indpb=mut_prob)

        self.toolbox = toolbox

    @staticmethod
    def uniform(bound_low, bound_up):
        """Generate random numbers between "low" and "up".

        If the arguments are lists, generates a list of values.

        Arguments:
            bound_low (list): lower bounds.
            bound_up (list): upper bounds.

        Returns:
            list: generated numbers.
        """
        return [random.uniform(a, b) for a, b in zip(bound_low, bound_up)]

    def eval_circuit(self, individuals):
        """Evaluate individuals and return the fitness and simulation results.

        This function also performs constraint handling, to penalize the
        individuals whose simulation results are not within the specifications
        defined in the configuration file. More info about the constraint
        handling can be found here:
        TODO: https://METER LINK CONSTRAINT HANDLING

        Arguments:
            individuals (list): list of individuals to evaluate. The number of
                individuals in the list is equal to the number of parallel
                simulations to perform.

        Raises:
            KeyError: If the received response type or format is invalid.
            TypeError: If the constraints limits are invalid.

        Returns:
            tuple: individuals' fitness and simulation results.
        """
        # A list with the variables of all individuals stored in dictionaries
        variables = []

        # Map the individual variables values to a dictionary with the
        # respective variable value and name
        for ind in individuals:
            variables.append({key: ind[idx] for idx, key in enumerate(self.circuit_vars)})

        # Send the request to the server
        req = dict(type='updateAndRun', data=variables)
        self.client.send_data(req)
        # Wait for data from server
        res = self.client.recv_data()

        try:
            res_type = res['type']
            sim_res = res['data']
        except KeyError as err:
            logger.error(err)

        if res_type != 'updateAndRun':
            raise KeyError("Simulation error!!! Check variables defaults, etc.")

        results = []

        # Get the fitnesses and simulation results for all individuals
        for idx in range(len(individuals)):
            fitness = []    # Fitnesses of one individual
            pen = 0         # Fitness Penalty

            sim_res_ind = sim_res[idx]  # Simulation results of one individual

            if self.constraints:
                for key, val in self.constraints.items():
                    # Try to compute the penalty (if constraint has two limits)
                    try:
                        # Try to convert the values to float
                        val_0 = float(val[0])
                        val_1 = float(val[1])

                        # Normalize the simulation result
                        if val_0 != val_1:
                            res_norm = (sim_res_ind[key] - val_0) / (val_1 - val_0)
                            # Check the limits
                            if res_norm < 0:
                                pen += self.penalty_delta - res_norm
                            elif res_norm > 1:
                                pen += self.penalty_delta + (res_norm - 1)
                        # If the limits are equal
                        elif val_0 == val_1 and sim_res_ind[key] != val_0:
                            pen += self.penalty_delta + math.fabs(sim_res_ind[key] - val_0)

                    # If contraint only has one limit
                    except ValueError:
                        # True - defined, false - undefined
                        limit = [True, True]

                        for lim, value in enumerate(val):
                            try:
                                # Get the constraint value and normalize it
                                res_norm = (sim_res_ind[key] / float(value)) - 1
                            # If can't convert to float, the limit is not defined
                            except ValueError:
                                limit[lim] = False

                        # If founds two limits, it should be handled in the previous 'try'
                        if limit[0] and limit[1]:
                            raise TypeError("Both limits exist.. it shouldn't be here!!!")

                        # If constraint has maximum allowed value
                        if not limit[0] and res_norm > 0:
                            pen += self.penalty_delta + res_norm

                        # If constraint has minimum allowed value
                        elif not limit[1] and res_norm < 0:
                            pen += self.penalty_delta - res_norm

            for key, val in self.objectives.items():
                try:
                    # Add the penalty weight to penalty
                    penalty = pen * self.penalty_weight

                    # Avoid overflow problems
                    if penalty > 500:
                        penalty = 500

                    # If the fitness is to maximize, change the penalty signal
                    if val > 0:
                        penalty = -penalty

                    tot_penalty = math.exp(self.penalty_weight*penalty)

                    # Get the simulation result
                    result = sim_res_ind[key]

                    # If the simulation result is negative, invert the penalty
                    if result < 0:
                        tot_penalty = 1 / tot_penalty

                    fitness.append(result * tot_penalty)
                except KeyError as err:
                    raise KeyError(
                        f"Eval circuit: there's no key {err} in the simulation results.")
                except OverflowError as err:
                    raise ValueError(f"Overflow error while evaluating the circuit: {err}")

            results.append((fitness, sim_res_ind))

            #print("FITNESS:", fitness)
            #print("SIM RES:", sim_res_ind)

        return results

    def ga_mu_plus_lambda(self, mu, lambda_, checkpoint_load, checkpoint_fname,
                          checkpoint_freq, sel_best, verbose):
        """The (mu + lambda) evolutionary algorithm.

        Adapted from: https://github.com/DEAP/deap/blob/master/deap/algorithms.py

        The pseudo-code goes as follows:
            evaluate(population)
            for g in range(ngen):
                offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)
                evaluate(offspring)
                population = select(population + offspring, mu)

        First, the individuals having an invalid fitness are evaluated. Second,
        the evolutionary loop begins by producing "lambda_" offspring from the
        population, the offspring are generated by the "varOr" function. The
        offspring are then evaluated and the next generation population is
        selected from both the offspring and the population. Finally, when
        "max_gen" generations are done, the algorithm returns a tuple with the
        final population and a "deap.tools.Logbook" of the evolution.
        This function expects "toolbox.mate", "toolbox.mutate", "toolbox.select",
        and "toolbox.evaluate" aliases to be registered in the toolbox.

        Arguments:
            mu (float): number of individuals to select for the next generation.
            lambda_ (int): number of children to produce at each generation.
            checkpoint_load (str or None): checkpoint file to load, if provided.
            checkpoint_fname (str): name of the checkpoint file to save.
            checkpoint_freq (str): checkpoint saving frequency (relative to gen).
            sel_best (int): number of best individuals to log at each generation.
            verbose (bool): run in verbosity mode.

        Returns:
            tuple: final population and the logbook of the evolution.
        """
        # Create the statistics
        stats_pop = tools.Statistics()
        stats_fit = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats_res = tools.Statistics(key=lambda ind: ind.result)
        stats = tools.MultiStatistics(population=stats_pop, fitness=stats_fit, result=stats_res)
        stats.register("value", copy.deepcopy)

        # If a checkpoint is provided, continue from the given generation
        if checkpoint_load:
            # Load the dictionary from the pickled file
            cp = file.read_pickle(checkpoint_load)
            # Load the stored parameters
            population = cp['population']
            start_gen = cp['generation'] + 1
            logbook = cp['logbook']
            random.setstate(cp['rnd_state'])
            logger.info("Running from a checkpoint!")
            logger.info("-- Population size: %d", len(population))
            logger.info("-- Current generation: %d\n", start_gen)

        else:  # Create the population
            population = self.toolbox.population(n=self.pop_size)
            start_gen = 1

            # Create the logbook
            logbook = tools.Logbook()
            logbook.header = 'gen', 'evals', 'population', 'fitness', 'result'

            # Get the individuals that are not evaluated
            invalid_inds = [ind for ind in population if not ind.fitness.valid]

            # The number of simulation calls to the server is the number of
            # invalid individuals
            num_sims = len(invalid_inds)

            logger.info("Starting the initial evaluation | evaluations: %d", num_sims)

            # Evaluation start time
            start_time = time.time()

            # Evaluate the individuals with an invalid fitness
            results = self.toolbox.evaluate(invalid_inds)

            for ind, res_ind in zip(invalid_inds, results):
                ind.fitness.values = res_ind[0]
                ind.result = res_ind[1]

            # Assign the crowding distance to the individuals (no selection is done)
            population = self.toolbox.select(population, len(population))

            record = stats.compile(population)
            logbook.record(gen=0, evals=num_sims, **record)

            # Evaluation time
            total_time = time.time() - start_time
            mins, secs = divmod(total_time, 60)
            hours, mins = divmod(mins, 60)
            msg = f"Finished generation. Elapsed time: {hours:02.0f}h{mins:02.0f}m{secs:02.0f}s"
            secs = total_time / num_sims
            mins, secs = divmod(secs, 60)
            msg += f" | avg: {mins:02.0f}m{secs:02.2f}s/ind\n"
            logger.info(msg)


        print("====================== Starting Optimization ======================\n")

        # Begin the generational process
        for gen in range(start_gen, self.max_gen + 1):
            # Vary the population
            offspring = algorithms.varOr(population, self.toolbox, lambda_, self.cx_prob,
                                         self.mut_prob)

            # Evaluate the individuals with an invalid fitness
            invalid_inds = [ind for ind in offspring if not ind.fitness.valid]

            # The number of simulation calls to the server is the number of
            # invalid individuals
            num_sims = len(invalid_inds)

            msg = f"Starting generation {gen}/{self.max_gen} | evaluations: {num_sims}"
            logger.info(msg)

            # Evaluation start time
            start_time = time.time()

            # Evaluate the individuals with an invalid fitness
            results = self.toolbox.evaluate(invalid_inds)

            for ind, res_ind in zip(invalid_inds, results):
                ind.fitness.values = res_ind[0]
                ind.result = res_ind[1]

            # Select the next generation population
            population[:] = self.toolbox.select(population + offspring, mu)

            # Update the statistics with the new population
            record = stats.compile(population)
            logbook.record(gen=gen, evals=num_sims, **record)

            # Save a checkpoint of the evolution
            if gen % checkpoint_freq == 0:
                cp = dict(generation=gen, population=population, logbook=logbook,
                          rnd_state=random.getstate())
                file.write_pickle(checkpoint_fname, cp)

            # Evaluation time
            total_time = time.time() - start_time
            mins, secs = divmod(total_time, 60)
            hours, mins = divmod(mins, 60)
            msg = f"Finished generation. "
            msg += f"Elapsed time: {hours:02.0f}h{mins:02.0f}m{secs:02.0f}s | "
            secs = total_time / num_sims
            mins, secs = divmod(secs, 60)
            msg += f"avg: {mins:02.0f}m{secs:02.2f}s/ind\n"
            logger.info(msg)

            # Show the best individuals of each generation
            print(f"---- Best {sel_best} individuals of this generation ----")

            best_inds = tools.selBest(population, sel_best)

            for i, ind in enumerate(best_inds):
                print(f"Ind #{i + 1} => ", end='')

                # Circuit variables/parameters
                formatted_params = [
                    f"{key}: {ind[idx]:.2g}" for idx, key in enumerate(self.circuit_vars)
                ]
                print(' | '.join(formatted_params))

                # Fitness
                print("\t  Fitness -> ", end='')
                formatted_fits = [
                    f"{key}: {ind.fitness.values[idx]:.2g}"
                    for idx, key in enumerate(list(self.objectives.keys()))
                ]
                print(' | '.join(formatted_fits))

                # Simulation results
                print("\t  Results -> ", end='')
                formatted_res = [
                    f"{key}: {val:.2g}"
                    for key, val in ind.result.items()
                ]
                print(' | '.join(formatted_res))
            print("")

        return population, logbook

    def run_ga(self, checkpoint_fname, mu=None, lambda_=None, checkpoint_load=None,
               checkpoint_freq=1, sel_best=5, verbose=True):
        """Wrapper for the "ga_mu_plus_lambda" function.

        Arguments:
            checkpoint_fname (str): name of the checkpoint file to save
            mu (int or None, optional): number of individuals to select for the
                next gen (default: None).
            lambda_ (int or None, optional): number of children to produce at
                each gen (default: None).
            checkpoint_load (str or None, optional): -ame of the checkpoint
                file to load, if provided (default: None).
            checkpoint_freq (int, optional): checkpoint saving frequency (gen
                per checkpoint) (default: 1).
            sel_best (int, optional): number of best individuals to log at each
                generation (default: 5).
            verbose (bool, optional): run in verbosity mode (default: True).

        Returns:
            tuple: pareto fronts and the logbook of the evolution.
        """
        # Evaluate mu and lambda_
        if mu is None:
            mu = self.pop_size
        if lambda_ is None:
            lambda_ = self.pop_size

        start_time = time.time()

        result, logbook = self.ga_mu_plus_lambda(
            mu=mu,
            lambda_=lambda_,
            checkpoint_load=checkpoint_load,
            checkpoint_fname=checkpoint_fname,
            checkpoint_freq=checkpoint_freq,
            sel_best=sel_best,
            verbose=verbose)

        # Get current date and time
        current_time = time.strftime("%H:%M:%S, %d of %B %Y", time.localtime())
        logger.info("Optimization finished at %s.", current_time)

        # ga_mu_plus_lambda execution time
        secs = time.time() - start_time
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        msg = f"Optimization total time: {hours:02.0f}h{mins:02.0f}m{secs:02.0f}s\n"
        logger.info(msg)

        # Get the pareto fronts from the optimization results
        fronts = tools.emo.sortLogNondominated(result, len(result))

        return fronts, logbook
