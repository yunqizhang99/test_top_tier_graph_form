import networkx as nx 
import alg2_parameters as parameters
import random
import matplotlib.pyplot as plt 

def alg2_form():

	G = nx.Graph()

	G.add_nodes_from(parameters.ALL_VALIDATORS)

	all_validators = parameters.ALL_VALIDATORS.copy()

	quorum_sets = parameters.QUORUM_SETS.copy()

	epoch_counter = 0

	while True:
		random.shuffle(all_validators)
		satisfied_counter = 0

		while len(all_validators) > 0:
			cur_validator = all_validators.pop()

			if len(list(nx.all_neighbors(G, cur_validator))) >= quorum_sets[cur_validator][0]:
				satisfied_counter += 1
				if satisfied_counter == parameters.TOTAL_NUM_OF_VALIDATORS:
					plt.figure(1)
					nx.draw_networkx(G, with_labels=True)
					plt.show()
					return "CONVERGED, " + "EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter), G
				continue

			rand_cand = random.choice(quorum_sets[cur_validator][1])
			try_find_cand_counter = 0
			while (rand_cand == cur_validator or rand_cand in list(nx.all_neighbors(G, cur_validator))) and try_find_cand_counter < parameters.TRY_FIND_CAND_LIMIT:
				rand_cand = random.choice(quorum_sets[cur_validator][1])
				try_find_cand_counter += 1

			if try_find_cand_counter >= parameters.TRY_FIND_CAND_LIMIT:
				continue

			G.add_edge(cur_validator, rand_cand)

		epoch_counter += 1
		print("EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter))
		
		all_validators = parameters.ALL_VALIDATORS.copy()

def alg2_prune(G):
	for i in range(0, parameters.TOTAL_NUM_OF_VALIDATORS-1):
		for j in range(i+1, parameters.TOTAL_NUM_OF_VALIDATORS):
			if G.has_edge(i, j) and len(list(nx.node_disjoint_paths(G, i, j))) >= 5:
				G.remove_edge(i, j)
	plt.figure(2)
	nx.draw_networkx(G, with_labels=True)
	plt.show()

if __name__=="__main__": 
    [graph_form_str, G] = alg2_form()
    print(graph_form_str)
    alg2_prune(G)

