import networkx as nx 
import alg1_parameters as parameters
import random
import matplotlib.pyplot as plt 

def alg1():

	G = nx.Graph()

	G.add_nodes_from(parameters.ALL_VALIDATORS)

	all_validators = parameters.ALL_VALIDATORS.copy()

	quorum_sets = parameters.QUORUM_SETS.copy()

	epoch_counter = 0
	bump_ups = 0
	last_bumpup_at = 0

	while True:
		random.shuffle(all_validators)
		satisfied_counter = 0

		while len(all_validators) > 0:
			cur_validator = all_validators.pop()

			if len(list(nx.all_neighbors(G, cur_validator))) >= quorum_sets[cur_validator][0]:
				satisfied_counter += 1
				if satisfied_counter == parameters.TOTAL_NUM_OF_VALIDATORS:
					nx.draw_networkx(G, with_labels=True)
					plt.show()
					return "CONVERGED, " + "EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter)
				continue

			rand_cand = random.choice(quorum_sets[cur_validator][1])
			try_find_cand_counter = 0
			while (rand_cand == cur_validator or len(list(nx.all_neighbors(G, rand_cand))) >= quorum_sets[rand_cand][0] + bump_ups or rand_cand in list(nx.all_neighbors(G, cur_validator))) and try_find_cand_counter < parameters.TRY_FIND_CAND_LIMIT:
				rand_cand = random.choice(quorum_sets[cur_validator][1])
				try_find_cand_counter += 1

			if try_find_cand_counter >= parameters.TRY_FIND_CAND_LIMIT:
				continue

			G.add_edge(cur_validator, rand_cand)

		epoch_counter += 1
		print("EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter))
		if epoch_counter > 10 and epoch_counter - last_bumpup_at > parameters.CAN_BUMP_UP:
			bump_ups += 1
			print("BUMPED!")
			last_bumpup_at = epoch_counter

		all_validators = parameters.ALL_VALIDATORS.copy()

if __name__=="__main__": 
    print(alg1())

