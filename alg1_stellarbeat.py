import networkx as nx 
import alg1_parameters as parameters
import random
import matplotlib.pyplot as plt
import stellarbeat
import ast

# for validator i, check if it is ok to connect to one validator in org with index j in its quorumset
def conn_org_eligible(G, i, j):
	if isinstance(G.nodes[i]['quorumset'][j], str):
		return not G.has_edge(i, G.nodes[i]['quorumset'][j]) and i != G.nodes[i]['quorumset'][j] and i in G.nodes[G.nodes[i]['quorumset'][j]]['quorumset_all_nodes']
	else:
		return G.nodes[i]['org_conn_book'][j] < G.nodes[i]['quorumset'][j][1]

# for validator i, check if it is ok to connect to validator j
def conn_cand_eligible(G, i, j):
	if i == j or G.has_edge(i, j) or i not in G.nodes[j]['quorumset_all_nodes']:
		return False, None
	i_org_in_j = None
	i_org_in_j_index = -1
	for count, item in enumerate(G.nodes[j]['quorumset']):
		if not isinstance(item, str):
			if i in item[0]:
				i_org_in_j = item
				i_org_in_j_index = count
				break
	count_j_conns_to_i_org = 0
	for item in i_org_in_j[0]:
		if G.has_edge(item, j):
			count_j_conns_to_i_org += 1
	if count_j_conns_to_i_org >= i_org_in_j[1] + G.nodes[j]['bump_ups']:
		return False, None
	return True, i_org_in_j_index

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

	total_num_validators = 0

	satisfied_counter = {}

	G = nx.Graph()
	all_validators = []

	for item in network_fetched:
		total_num_validators += 1
		satisfied_counter[item['publicKey']] = 0
		all_validators.append(item['publicKey'])
		quorumset_all_nodes, quorumset, org_target_conn_num = get_target_conns(network_fetched, item['publicKey'])
		org_conn_book = [0] * len(quorumset)
		G.add_node(item['publicKey'], quorumset_all_nodes = quorumset_all_nodes, quorumset = quorumset, org_target_conn_num = org_target_conn_num, org_conn_book = org_conn_book, last_bumpup_at = 0, bump_ups = 0)

	epoch_counter = 0

	all_validators_copy = all_validators.copy()

	while True:
		random.shuffle(all_validators_copy)

		while len(all_validators_copy) > 0:
			cur_validator = all_validators_copy.pop()

			cur_validator_num_satisfied_orgs = 0
			for i in range(0, len(G.nodes[cur_validator]['quorumset'])):
				if isinstance(G.nodes[cur_validator]['quorumset'][i], str):
					if G.nodes[cur_validator]['org_conn_book'][i] == 1:
						cur_validator_num_satisfied_orgs += 1
				else:
					if G.nodes[cur_validator]['org_conn_book'][i] >= G.nodes[cur_validator]['quorumset'][i][1]:
						cur_validator_num_satisfied_orgs += 1
			if cur_validator_num_satisfied_orgs >= G.nodes[cur_validator]['org_target_conn_num']:
				satisfied_counter[cur_validator] = 1
				if epoch_counter > 20 and epoch_counter - G.nodes[cur_validator]['last_bumpup_at'] > parameters.CAN_BUMP_UP:
					G.nodes[cur_validator]['bump_ups'] += 1
					print("BUMPED!")
					G.nodes[cur_validator]['last_bumpup_at'] = epoch_counter
				# if all validators are satisfied
				if sum(satisfied_counter.values()) == total_num_validators:
					# nx.draw_networkx(G, with_labels=True)
					# plt.show()
					return "CONVERGED, " + "EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter), G
				# if cur_validator is satisfied but not all validators
				continue

			rand_cand_validator = None

			rand_cand_org = random.randint(0, len(G.nodes[cur_validator]['quorumset'])-1)
			try_find_cand_counter = 0
			while not conn_org_eligible(G, cur_validator, rand_cand_org) and try_find_cand_counter <= len(G.nodes[cur_validator]['quorumset'])*2:
				rand_cand_org = random.randint(0, len(G.nodes[cur_validator]['quorumset'])-1)
				try_find_cand_counter += 1
			if try_find_cand_counter > len(G.nodes[cur_validator]['quorumset'])*2:
				continue

			if not isinstance(G.nodes[cur_validator]['quorumset'][rand_cand_org], str):
				rand_cand_validator = random.choice(G.nodes[cur_validator]['quorumset'][rand_cand_org][0])
				try_find_cand_counter = 0    
				conn_cand_eligibility, cur_validator_in_rand_cand_validator_org_index = conn_cand_eligible(G, cur_validator, rand_cand_validator)
				while not conn_cand_eligibility and try_find_cand_counter <= len(G.nodes[cur_validator]['quorumset'][rand_cand_org][0])*2:
					rand_cand_validator = random.choice(G.nodes[cur_validator]['quorumset'][rand_cand_org][0])
					conn_cand_eligibility, cur_validator_in_rand_cand_validator_org_index = conn_cand_eligible(G, cur_validator, rand_cand_validator)
					try_find_cand_counter += 1
				if try_find_cand_counter > len(G.nodes[cur_validator]['quorumset'][rand_cand_org][0])*2:
					continue
			else:
				rand_cand_validator = G.nodes[cur_validator]['quorumset'][rand_cand_org]
				cur_validator_in_rand_cand_validator_org_index = rand_cand_org

			G.add_edge(cur_validator, rand_cand_validator)
			G.nodes[cur_validator]['org_conn_book'][rand_cand_org] += 1
			G.nodes[rand_cand_validator]['org_conn_book'][cur_validator_in_rand_cand_validator_org_index] += 1

			# print("EPOCH: " + str(epoch_counter) + " " + "SATISFIED: " + str(satisfied_counter))

		epoch_counter += 1
		print("EPOCH: " + str(epoch_counter) + ", SATISFIED VALIDATORS: " + str(sum(satisfied_counter.values())))
		if epoch_counter == 100:
			nx.draw_networkx(G, with_labels=False)
			plt.show()

		all_validators_copy = all_validators.copy()

if __name__=="__main__": 
	network_fetched = stellarbeat._fetch_from_url()

	alg1(network_fetched)


	# print("---")
	# print(quorumset_all_nodes)
	# print("---")
	# print(quorumset)
	# print("---")
	# print(org_target_conn_num )


