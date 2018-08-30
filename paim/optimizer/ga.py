# -*- coding: utf-8 -*-
"""Genetic algrithm using DEAP"""

import array
import copy
import math
import pickle
import random
import textwrap

from deap import algorithms, base, creator, tools
from profilehooks import timecall
from tqdm import tqdm


# Organize everything in the class
class OptimizerNSGA2:
    """A simulation-based circuit optimizer based on the NSGA2 algorithm

    This optimizer is based on DEAP and requires connection to a circuit
    simulation environment (e.g. Cadence Virtuoso). It was designed to be
    circuit and simulator independent, requiring only the optimization
    objectives and constraints, and the circuit variables.
    After finishing the optimization, it returns the optimal pareto front
    and the logbook.

    DEAP source: https://deap.readthedocs.io/en/master/

    Arguments:
        objectives {dict} -- Optimization objectives (fitness)
        constraints {dict} -- Optimization constraints (circuit requirements)
        circuit_vars {dict} -- Circuit design variables
        pop_size {int} -- Population size
        max_gen {int} -- Max generations

    Keyword Arguments:
        client {handler} -- The client that communicates with the simulator (default: None)
        mut_prob {float} -- Probability of mutation (default: 0.1)
        cx_prob {float} -- Probability of crossover (default: 0.8)
        mut_eta {int} -- Crowding degree of the mutation (default: 20)
        cx_eta {int} -- Crowding degree of the crossover (default: 20)
        debug {bool} -- Debug(default: False)
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, objectives, constraints, circuit_vars, pop_size,
                 max_gen, sim_multi, client=None, mut_prob=0.1, cx_prob=0.8,
                 mut_eta=20, cx_eta=20, debug=False):
        """Create the Optimizer"""

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
        self.sim_multi = sim_multi

        if client is not None:
            self.client = client

        # Set bounds
        bound_low = []
        bound_up = []
        # Get the bounds from the circuit_vars
        for val in circuit_vars.values():
            bound_low.append(val[0])
            bound_up.append(val[1])

        # Define the Fitness
        fitness_weights = tuple(objectives.values())
        creator.create("FitnessMulti", base.Fitness, weights=fitness_weights)
        # Define an individual
        creator.create("Individual", array.array, typecode='d',
                       fitness=creator.FitnessMulti)

        toolbox = base.Toolbox()

        # float gerado aleatoriamente
        toolbox.register("attr_float", self.uniform, bound_low, bound_up)
        # Define individuo como a lista de floats (itera pelo "attr_float"
        # e coloca o resultado no "creator.Individual")
        toolbox.register("individual", tools.initIterate,
                         creator.Individual, toolbox.attr_float)
        # Define a população como uma lista de individuos (o nro de individuos
        # só é definido quando se inicializa a pop)
        toolbox.register("population", tools.initRepeat,
                         list, toolbox.individual)

        # operator for selecting individuals for breeding the next generation
        toolbox.register("select", tools.selNSGA2)

        # Parallel processing
        #toolbox.register("map", Pool().map)

        # register the goal / fitness function
        toolbox.register("evaluate", self.eval_circuit)
        # The constraints handling is made in the "eval_circuit" function
        ##self.toolbox.decorate("evaluate", (self.feasibility, 0, self.distance))

        # register the crossover operator
        toolbox.register("mate", tools.cxSimulatedBinaryBounded,
                         low=bound_low, up=bound_up, eta=cx_eta)

        # register the mutation operator
        toolbox.register("mutate", tools.mutPolynomialBounded,
                         low=bound_low, up=bound_up,
                         eta=mut_eta, indpb=mut_prob)

        self.toolbox = toolbox

    @staticmethod
    def uniform(bound_low, bound_up):
        """Generate a random number between "low" and "up". If the arguments
        are a list, it generates a list.

        Arguments:
            low {list} -- Lower bounds
            up {list} -- Upper bounds

        Returns:
            {list} -- Generated numbers
        """
        return [random.uniform(a, b) for a, b in zip(bound_low, bound_up)]

    ##################################################################
    ##################################################################
    ##################################################################
    ##################################################################

    # def handle_constraints(self, sim_res):

    #     # Comparar constraints com res_sim...

    #     # Baixar fitness de acordo com o resultado obtido.
    #     # NOTA: Ver https://www.sciencedirect.com/science/article/pii/S0045782501003231
    #     penalty = 1
    #     return penalty

    # https://groups.google.com/forum/#!topic/deap-users/SSd_zZ4XinI
    def eval_circuit(self, individuals):
        """Evaluate the individuals and return their fitness
        
        Arguments:
            individuals {list} -- List of individuals to evaluate
        """
        # TODO: UPDATE DO DOCSTRING

       # A list with the variables of all individuals stored in dictionaries
        variables = []

        # Map the individual variables values to a dictionary with the
        # respective variable value and name
        for ind in individuals:
            variables.append(
                {key: ind[idx] for idx, key in enumerate(self.circuit_vars)})

        # Send the request to the server
        req = dict(type='updateAndRun', data=variables)
        self.client.send_data(req)
        # Wait for data from server
        res = self.client.recv_data()

        try:
            res_type = res['type']
            sim_res = res['data']
        except KeyError as err:  # if the key does not exist
            print(f"Error: {err}")

        if res_type != 'updateAndRun':
            raise Exception(
                "[ERROR] Simulation error!!! Check variables defaults, etc.")

        fitnesses = []

        # Get the fitnesses for all individuals
        for idx in range(len(individuals)):
            fitness = []    # Fitnesses of one individual

            sim_res_ind = sim_res[idx]  # Simulation results of one individual

            for obj in self.objectives.keys():
                try:
                    fitness.append(sim_res_ind[obj])
                except KeyError as err:
                    raise Exception(
                        f"Eval circuit: there's no key {err} in the simulation results.")

            # For now the penalty is applied with the same weight to all the objectives, but we
            # can change this later for better performance
            penalty = 1

            if self.constraints:
                # Handling the contraints
                # TODO: Just a test... se não estiverem na saturação
                if sim_res_ind["REG1"] != 2 or sim_res_ind["REG2"] != 2:
                    penalty = 0.01

            # Multiply the fitness by the penalty
            #fitnesses = [fit * penalty for fit in fitnesses]
            # TODO: Talvez verificar se o penalty for para minimizar ou maximizar
            # e atribuir o penalty de acordo
            fitness = [(1/penalty) * fitness[0], penalty * fitness[1]]

            fitnesses.append(tuple(fitness))

            #print(f"FITNESS: {fitness}")
            #print(f"VARS: {individuals[idx]}")
            #print(f"RESULTS: {sim_res_ind}")
            # print("==================================================")

        return fitnesses

    @timecall
    def ga_mu_plus_lambda(self, mu, lambda_, checkpoint_fname, checkpoint_freq,
                          checkpoint, verbose, sel_best):
        """This is the (mu + lambda) evolutionary algorithm.
        ADAPTED FROM: https://github.com/DEAP/deap/blob/master/deap/algorithms.py

        The pseudocode goes as follow ::
            evaluate(population)
            for g in range(ngen):
                offspring = varOr(population, toolbox, lambda_, cxpb, mutpb)
                evaluate(offspring)
                population = select(population + offspring, mu)
        First, the individuals having an invalid fitness are evaluated. Second,
        the evolutionary loop begins by producing *lambda_* offspring from the
        population, the offspring are generated by the :func:`varOr` function. The
        offspring are then evaluated and the next generation population is
        selected from both the offspring **and** the population. Finally, when
        *ngen* generations are done, the algorithm returns a tuple with the final
        population and a :class:`~deap.tools.Logbook` of the evolution.
        This function expects :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
        :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
        registered in the toolbox. This algorithm uses the :func:`varOr`
        variation.
        """
        # TODO: FAZER DOCSTRING EM CONDIÇÕES

        # Create the statistics
        stats_pop = tools.Statistics()
        stats_fit = tools.Statistics(key=lambda ind: ind.fitness.values)
        stats = tools.MultiStatistics(population=stats_pop, fitness=stats_fit)
        stats.register("value", copy.deepcopy)

        # If a checkpoint is provided, continue the given generation
        if checkpoint:
            with open(checkpoint, 'rb') as f:   # Load the checkpoint file
                cp = pickle.load(f)
            # Load the stored parameters
            population = cp["population"]
            start_gen = cp["generation"] + 1
            logbook = cp["logbook"]
            random.setstate(cp["rnd_state"])
            print(textwrap.dedent(f"""
                ======== Running from a checkpoint ========
                -- Population size: {len(population)}
                -- Current generation: {start_gen}"""))

        else:
            # Create the population
            population = self.toolbox.population(n=self.pop_size)
            start_gen = 1

            # Create the logbook
            logbook = tools.Logbook()
            logbook.header = 'gen', 'evals', 'population', 'fitness'

            # Get the individuals that are not evaluated
            invalid_inds = [ind for ind in population if not ind.fitness.valid]

            # Determine the number of simulation calls to the server
            n_sim = math.ceil(len(invalid_inds) / self.sim_multi)

            invalid_inds_multi = []

            # Split the individuals in groups of sim_multi
            for idx in range(n_sim):
                invalid_inds_multi.append(
                    invalid_inds[(self.sim_multi*idx):(self.sim_multi*(1+idx))])

            if verbose:
                print(f"\n======== Evaluating the initial population ({len(invalid_inds)} inds) | {self.sim_multi} evals/run (max) ========")
            else:
                 print("\n[INFO] Evaluating the initial population")

            # Evaluate the individuals with an invalid fitness
            # Fitnesses are the concatenation (sum) of all the fitnesses returned by "eval_circuit"
            fitnesses = sum(map(self.toolbox.evaluate,
                                tqdm(invalid_inds_multi, desc="Runs", unit="run", disable=(not verbose))), [])

            for ind, fit in zip(invalid_inds, fitnesses):
                ind.fitness.values = fit

            # Assign the crowding distance to the individuals (no selection is done)
            population = self.toolbox.select(population, len(population))

            record = stats.compile(population)
            logbook.record(gen=0, evals=len(invalid_inds), **record)

        print("\n====================== Starting Optimization ======================")

        # Begin the generational process
        for gen in range(start_gen, self.max_gen + 1):
            # Vary the population
            offspring = algorithms.varOr(population, self.toolbox, lambda_,
                                         self.cx_prob, self.mut_prob)

            # Evaluate the individuals with an invalid fitness
            invalid_inds = [ind for ind in offspring if not ind.fitness.valid]

            # Determine the number of simulation calls to the server
            n_sim = math.ceil(len(invalid_inds) / self.sim_multi)

            invalid_inds_multi = []

            # Split the individuals in groups of sim_multi
            for idx in range(n_sim):
                invalid_inds_multi.append(
                    invalid_inds[(self.sim_multi*idx):(self.sim_multi*(1+idx))])

            if verbose:
                print(f"\n======== Generation {gen}/{self.max_gen} | {len(invalid_inds)} evals | {self.sim_multi} evals/run (max) ========")

            # Evaluate the individuals with an invalid fitness
            # Fitnesses are the concatenation (sum) of all the fitnesses returned by "eval_circuit"
            fitnesses = sum(map(self.toolbox.evaluate,
                                tqdm(invalid_inds_multi, desc="Runs", unit="run", disable=(not verbose))), [])

            for ind, fit in zip(invalid_inds, fitnesses):
                ind.fitness.values = fit

            # Select the next generation population
            population[:] = self.toolbox.select(population + offspring, mu)

            # Update the statistics with the new population
            record = stats.compile(population)
            logbook.record(gen=gen, evals=len(invalid_inds), **record)

            # Save a checkpoint of the evolution
            if gen % checkpoint_freq == 0:
                cp = dict(population=population, generation=gen,
                          logbook=logbook, rnd_state=random.getstate())
                with open(checkpoint_fname, 'wb') as f:
                    pickle.dump(cp, f)

            # Show the best individuals of each generation
            if verbose:
                print(f"\n---- Best {sel_best} individuals of this generation ----")

                best_inds = tools.selBest(population, sel_best)

                for i, ind in enumerate(best_inds):
                    print(f"Ind #{i + 1} => ", end='')

                    formatted_params = [f"{key}: {ind[idx]:.2g}"
                                        for idx, key in enumerate(self.circuit_vars)]
                    print(' | '.join(formatted_params))

                    formatted_fits = [f"{key}: {ind.fitness.values[idx]:.2g}"
                                      for idx, key in enumerate(list(self.objectives.keys()))]
                    print(' | '.join(formatted_fits))

        print("\n====================== Optimization Finished ======================\n")

        return population, logbook

    def run_ga(self, checkpoint_fname, checkpoint_freq=1,
               checkpoint=None, verbose=True, sel_best=3):
        """Wrapper for the 'ga_mu_plus_lambda' function

        Arguments:
            checkpoint_fname {string} -- Name of the checkpoint file

        Keyword Arguments:
            checkpoint_freq {int} -- Number of generations per checkpoint saving (default: 1)
            checkpoint {string} -- Name of a checkpoint file to continue the evolution
                                   from. If None, start a new evolution (default: None)
            verbose {bool} -- Show info and logs (default: True)
            sel_best {int} -- The <sel_best> individuals to show at the end of a gen (default: 3)
        """
        result, logbook = self.ga_mu_plus_lambda(mu=self.pop_size, lambda_=self.pop_size,
                                                 checkpoint_fname=checkpoint_fname,
                                                 checkpoint_freq=checkpoint_freq,
                                                 checkpoint=checkpoint,
                                                 verbose=verbose, sel_best=sel_best)

        fronts = tools.emo.sortLogNondominated(result, len(result))

        return fronts, logbook
