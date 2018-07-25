# -*- coding: utf-8 -*-
"""Genetic algrithm using DEAP"""

import array
import copy
import random
import time

from deap import algorithms, base, creator, tools
from profilehooks import timecall

#from multiprocessing import Pool


# A class é só para ter tudo mais organizado...


class OptimizerNSGA2:
    """A simulation-based circuit optimizer based on the NSGA2 algorithm

    This optimizer is based on DEAP and requires connection to a circuit
    simulation environment (e.g. Cadence Virtuoso). It was designed to be
    circuit and simulator independent, requiring only the optimization
    objectives and constraints, and the circuit variables.
    After finishing the optimization, it returns the optimal pareto front
    and the logbook.

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
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, objectives, constraints, circuit_vars, pop_size,
                 max_gen, client=None, mut_prob=0.1, cx_prob=0.8,
                 mut_eta=20, cx_eta=20):
        """Create the Optimizer"""

        # INFO: The sum of mut_prob and cx_prob shall be in [0, 1]
        self.mut_prob = mut_prob
        self.cx_prob = cx_prob
        self.objectives = objectives
        self.constraints = constraints
        self.circuit_vars = list(circuit_vars.keys())
        self.pop_size = pop_size
        self.max_gen = max_gen

        if client is not None:
            self.client = client

        # Set bounds
        bound_low = []
        bound_up = []

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
            low {list} -- lower bounds
            up {list} -- upper bounds

        Returns:
            {list} -- Generated numbers
        """
        return [random.uniform(a, b) for a, b in zip(bound_low, bound_up)]

    ##################################################################
    ##################################################################
    ##################################################################
    ##################################################################

    # def run_simulation(self, client, individual):

    #     # res = ...
    #     res = 1
    #     return res

    # def handle_constraints(self, sim_res):

    #     # Comparar constraints com res_sim...

    #     # Baixar fitness de acordo com o resultado obtido.
    #     # NOTA: Ver https://www.sciencedirect.com/science/article/pii/S0045782501003231
    #     penalty = 1
    #     return penalty

    # https://groups.google.com/forum/#!topic/deap-users/SSd_zZ4XinI
    def eval_circuit(self, individual):
        """[summary]

        Arguments:
            individual {[type]} -- [description]
            client {[type]} -- [description]
            objectives {[type]} -- [description]

        Keyword Arguments:
            constraints {[type]} -- [description] (default: {None})

        Raises:
            Exception -- [description]

        Returns:
            [type] -- [description]
        """

        # Run simulation (j)

        variables = {}

        for idx, key in enumerate(self.circuit_vars):
            variables[key] = individual[idx]

        req = dict(type='updateAndRun', data=variables)
        self.client.send_data(req)

        #
        # Wait for data from server
        #
        res = self.client.recv_data()

        try:
            res_type = res['type']
            sim_res = res['data']
        except KeyError as err:  # if the key does not exist
            print(f"Error: {err}")

        if res_type != 'updateAndRun':
            print("Simulation error!!!")
            fitnesses = [1000, -1000]
            return tuple(fitnesses)

        fitnesses = []

        # Get the fitnesses
        for obj in self.objectives.keys():
            try:
                fitnesses.append(sim_res[obj])
            except KeyError as err:
                raise Exception(
                    f"Eval circuit: there's no key {err} in the simulation results.")

        
        # For now the penalty is applied with the same weight to all the objectives, but we
        # can change this later for better performance
        penalty = 1
        
        if self.constraints:
            # Handling the contraints
            # Just a test... se não estiverem na saturação
            if sim_res["REG1"] != 2 or sim_res["REG2"] != 2:
                penalty = 0.1

        # Multiply the fitness by the penalty
        #fitnesses = [fit * penalty for fit in fitnesses]
        #TODO: Talvez verificar se o penalty for para minimizar ou maximizar
        # e atribuir o penalty de acordo
        fitnesses = [(1/penalty) * fitnesses[0], penalty * fitnesses[1]]
            
        print(f"FITNESS: {fitnesses}")
        print(f"VARS: {individual}")
        print(f"RESULTS: {sim_res}")
        print("==================================================")

        return tuple(fitnesses)

    ##################################################################
    ##################################################################
    ##################################################################
    ##################################################################

    @timecall
    def ga_mu_plus_lambda(self, mu, lambda_, statistics,
                          halloffame=None, verbose=__debug__):
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
        # Create the population
        population = self.toolbox.population(n=self.pop_size)
        population = self.toolbox.select(population, len(population))

        # Create the statistics
        if statistics:
            stats = tools.Statistics()
            stats.register("pop", copy.deepcopy)

        # Create the logbook
        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats is not None else {}
        logbook.record(gen=0, nevals=len(invalid_ind), **record)

        # if verbose:
        #    print logbook.stream

        # Begin the generational process
        for gen in range(1, self.max_gen + 1):
            # Get current time
            start_time = time.time()

            # Vary the population
            offspring = algorithms.varOr(population, self.toolbox, lambda_,
                                         self.cx_prob, self.mut_prob)

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Select the next generation population
            population[:] = self.toolbox.select(population + offspring, mu)

            # Update the statistics with the new population
            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(invalid_ind), **record)
            if verbose:   # Only prints multiples of 5 gens (and not gen % 5)
                # print(logbook.stream)
                gen_time = time.time() - start_time
                print(f"-------- Gen: {gen}   |   # Evals: {len(invalid_ind)}   |   Time: {gen_time:.2f}s --------")

        return population, logbook

    def run_ga(self, stats=False, verbose=False):
        """[summary]

        Keyword Arguments:
            stats {bool} -- [description] (default: {False})
            verbose {bool} -- [description] (default: {False})

        Returns:
            [type] -- [description]
        """
        result, logbook = self.ga_mu_plus_lambda(mu=self.pop_size, lambda_=self.pop_size,
                                                 statistics=stats, verbose=verbose)

        fronts = tools.emo.sortLogNondominated(result, len(result))

        return fronts, logbook
