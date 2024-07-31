import networkx as nx 
import alg1_parameters as parameters
import random
import matplotlib.pyplot as plt 

def conn_cand_elgibile(G, i, j, bumps, target_conns):
	if i == j:
		return False
	i_table = list(nx.all_neighbors(G, i))
	if j in i_table:
		return False
	j_table = list(nx.all_neighbors(G, j))
	i_target_table = target_conns[i][1]
	j_target_table = target_conns[j][1]
	i_target_num = target_conns[i][0]
	j_target_num = target_conns[j][0]
	if len([peer for peer in j_table if peer in j_target_table]) < j_target_num and i in j_target_table:
		return True
	if len([peer for peer in j_table if peer in j_target_table]) >= j_target_num and len([peer for peer in j_table if peer not in j_target_table]) < bumps and i in j_target_table:
		return True

def alg1():

	G = nx.Graph()

	G.add_nodes_from(parameters.ALL_VALIDATORS)

	all_validators = parameters.ALL_VALIDATORS.copy()

	target_conns = parameters.TARGET_CONNS.copy()

	epoch_counter = 0
	bump_ups = 0
	last_bumpup_at = 0

	while True:
		random.shuffle(all_validators)
		satisfied_counter = [0]*parameters.TOTAL_NUM_OF_VALIDATORS

		while len(all_validators) > 0:
			cur_validator = all_validators.pop()

			if len([peer for peer in list(nx.all_neighbors(G, cur_validator)) if peer in target_conns[cur_validator][1]]) >= target_conns[cur_validator][0]:
				satisfied_counter[cur_validator] = 1
				if sum(satisfied_counter) == parameters.TOTAL_NUM_OF_VALIDATORS:
					nx.draw_networkx(G, with_labels=True)
					plt.show()
					return "CONVERGED, " + "EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter), G
				continue

			rand_cand = random.choice(target_conns[cur_validator][1])
			try_find_cand_counter = 0
			while not conn_cand_elgibile(G, cur_validator, rand_cand, bump_ups, target_conns) and try_find_cand_counter < parameters.TRY_FIND_CAND_LIMIT:
				rand_cand = random.choice(target_conns[cur_validator][1])
				try_find_cand_counter += 1

			if try_find_cand_counter >= parameters.TRY_FIND_CAND_LIMIT:
				continue

			G.add_edge(cur_validator, rand_cand)

		if epoch_counter == 10000:
			nx.draw_networkx(G, with_labels=True)
			plt.show()

		epoch_counter += 1
		print("EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter))
		if epoch_counter > 10 and epoch_counter - last_bumpup_at > parameters.CAN_BUMP_UP:
			bump_ups += 1
			print("BUMPED!")
			last_bumpup_at = epoch_counter

		all_validators = parameters.ALL_VALIDATORS.copy()

if __name__=="__main__": 
	s, G = alg1()
	print(s)
	# max_degs = []
	# avg_degs = []
	# diameters = []
	# min_v_cuts = []
	# for i in range(0, 1000):
	# 	print(i)
	# 	s, G = alg1()
	# 	G_degs = []
	# 	for node in G:
	# 		G_degs.append(G.degree[node])
	# 	avg_degs.append(sum(G_degs)/len(G_degs))
	# 	max_degs.append(max(G_degs))
	# 	diameters.append(nx.diameter(G))
	# 	min_v_cuts.append(len(nx.minimum_node_cut(G)))
	# fig, axes = plt.subplots(1, 4)
	# axes[0].hist(max_degs)
	# axes[1].hist(avg_degs)
	# axes[2].hist(diameters)
	# axes[3].hist(min_v_cuts)
	# plt.show()

