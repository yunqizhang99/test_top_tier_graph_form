import networkx as nx 
import alg1_parameters as parameters
import random
import matplotlib.pyplot as plt
import stellarbeat
import ast

def conn_cand_eligible(G, i, j, bumps, target_conns):
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

# get the target connection table and all nodes in the quorumset of node pk
def get_target_conns(network_fetched, pk):
	node_info = None

	for item in network_fetched:
		if item['publicKey'] == pk:
			node_info = item

	org_threshold = node_info['quorumSet']['threshold']

	quorumset_all_nodes = []
	quorumset = []

	for item in node_info['quorumSet']['validators']:
		quorumset_all_nodes.append(item)
		quorumset.append(item)
	for item in node_info['quorumSet']['innerQuorumSets']:
		quorumset_all_nodes.extend(item['validators'])
		inner_target_conn_num = len(item['validators']) - item['threshold'] + 1
		quorumset.append([item['validators'], inner_target_conn_num])

	org_target_conn_num = len(quorumset) - org_threshold + 3

	return quorumset_all_nodes, quorumset, org_target_conn_num

def alg1(network_fetched):

	G = nx.Graph()
	all_validators = []

	for item in network_fetched:
		all_validators.append(item['publicKey'])
		quorumset_all_nodes, quorumset, org_target_conn_num = get_target_conns(network_fetched, item['publicKey'])
		G.add_node(item['publicKey'], quorumset_all_nodes = quorumset_all_nodes, quorumset = quorumset, org_target_conn_num = org_target_conn_num, last_bumpup_at = -1, bump_ups = cur_node_bump_ups, satisfied = False)

	epoch_counter = 0

	while True:
		random.shuffle(all_validators)
		satisfied_counter = 0

		while len(all_validators) > 0:
			cur_validator = all_validators.pop()

			if G.nodes[cur_validator]['satisfied']:
				satisfied_counter += 1
				if sum(satisfied_counter) == parameters.TOTAL_NUM_OF_VALIDATORS:
					# nx.draw_networkx(G, with_labels=True)
					# plt.show()
					return "CONVERGED, " + "EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter), G
				continue

			rand_cand = random.choice(target_conns[cur_validator][1])
			try_find_cand_counter = 0    
			while not conn_cand_eligible(G, cur_validator, rand_cand, bump_ups, target_conns) and try_find_cand_counter < parameters.TRY_FIND_CAND_LIMIT:
				rand_cand = random.choice(target_conns[cur_validator][1])
				try_find_cand_counter += 1

			if try_find_cand_counter >= parameters.TRY_FIND_CAND_LIMIT:
				continue

			G.add_edge(cur_validator, rand_cand)

		if epoch_counter == 10000:
			nx.draw_networkx(G, with_labels=True)
			plt.show()

		epoch_counter += 1
		# print("EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter))
		if epoch_counter > 10 and epoch_counter - last_bumpup_at > parameters.CAN_BUMP_UP:
			bump_ups += 1
			# print("BUMPED!")
			last_bumpup_at = epoch_counter

		all_validators = parameters.ALL_VALIDATORS.copy()

if __name__=="__main__": 
	network_fetched = stellarbeat._fetch_from_url()
	get_target_conns(network_fetched, 'GD6SZQV3WEJUH352NTVLKEV2JM2RH266VPEM7EH5QLLI7ZZAALMLNUVN')


