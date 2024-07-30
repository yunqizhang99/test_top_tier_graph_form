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
		target_conns_cands.append(item)
		quorumset_all_nodes.extend(item['validators'])
		conns_cands_dict[str([item['validators'], len(item['validators']) - item['threshold'] + 1])] = 0
	org_target_conn_num = len(target_conns_cands) - org_threshold + 1
	target_conns_orgs = random.sample(target_conns_cands, org_target_conn_num)

	target_conns_by_node = []
	for item in target_conns_orgs:
		if isinstance(item, str):
			target_conns_by_node.append(item)
			# print(item)
		else:
			inner_threshold = item['threshold']
			inner_target_conn_num = len(item['validators']) - inner_threshold + 1
			target_conns_in_inner = random.sample(item['validators'], inner_target_conn_num)
			target_conns_by_node.extend(target_conns_in_inner)
			# print(target_conns_in_inner)

	# print(len(target_conns_by_node))
	# print(conns_cands_dict)
	# print(quorumset_all_nodes)

	return len(target_conns_by_node), conns_cands_dict, quorumset_all_nodes

def alg1(network_fetched):

	G = nx.Graph()
	all_validators = []

	for item in network_fetched:
		all_validators.append(item['publicKey'])
		num_target_conns, conns_cands_dict, quorumset_all_nodes = get_target_conns(network_fetched, item['publicKey'])
		G.add_node(item['publicKey'], num_target_conns = num_target_conns, conns_cands_dict = conns_cands_dict, quorumset_all_nodes = quorumset_all_nodes, epoch_counter = 0, last_bumpup_at = -1, bump_ups = cur_node_bump_ups)

	satisfied_counter = {}
	for item in all_validators:
		satisfied_counter[item] = 0

	while True:
		random.shuffle(all_validators)
		satisfied_counter = dict.fromkeys(sa, 0)

		while len(all_validators) > 0:
			cur_validator = all_validators.pop()

			if sum(G.nodes[cur_validator]['conns_cands_dict'].values()) >= G.nodes[cur_validator]['num_target_conns']:
				satisfied_counter[cur_validator] = 1
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


