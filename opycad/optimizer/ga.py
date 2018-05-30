# -*- coding: utf-8 -*-
"""Genetic algrithm using DEAP"""

import random

from deap import base
from deap import creator
from deap import tools

# Create the classes
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

IND_SIZE = 10

# This toolbox will store all the objects (individual, population, functions, etc.)
toolbox = base.Toolbox()
# Attribute generator (generates integer between 0 and 1)
toolbox.register("attr_bool", random.randint, 0, 1)

# Structure initializers
# Instantiate individual (initialized 100 times)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, 100)
# Instantiate population
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def eval_one_max(individual):
    