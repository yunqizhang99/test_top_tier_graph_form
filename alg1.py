import networkx as nx 
import alg1_parameters as parameters
import random

G = nx.Graph()

G.add_nodes_from(parameters.ALL_VALIDATORS)

all_validators = parameters.ALL_VALIDATORS.copy()

random.shuffle(all_validators)

while len(all_validators) > 0:
	