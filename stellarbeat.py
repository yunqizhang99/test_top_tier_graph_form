import json
import os
from requests import get
from platformdirs import user_cache_dir

def _fetch_from_url() -> list:
    """
    Get data from stellarbeat, filter out non-validator nodes, and return a list of dicts with two keys: 'publicKey' and 'quorumSet'.
    """
    url = "https://api.stellarbeat.io/v1/node"
    response = get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        return [{'publicKey': node['publicKey'], 'quorumSet': node['quorumSet'], 'organizationId': node['organizationId']}
            for node in data if node['isValidator']]
    else:
        response.raise_for_status()

def create_fake_nodes(n) -> list:
    """
    Create n fake nodes and put them in a list
    """
    all_fake_nodes = []
    res = []
    for i in range(0, n):
        pk = "MALICIOUS" + str(i)
        all_fake_nodes.append(pk)
    for i in range(0, n):
        pk = "MALICIOUS" + str(i)
        cur_node_validators = all_fake_nodes.copy()
        cur_node_validators.remove(pk)
        qs = {'threshold': 5, 'validators': [], 'innerQuorumSets': [{'threshold': 2, 'validators': ['GAAV2GCVFLNN522ORUYFV33E76VPC22E72S75AQ6MBR5V45Z5DWVPWEU', 'GAVXB7SBJRYHSG6KSQHY74N7JAFRL4PFVZCNWW2ARI6ZEKNBJSMSKW7C', 'GAYXZ4PZ7P6QOX7EBHPIZXNWY4KCOBYWJCA4WKWRKC7XIUS3UJPT6EZ4'], 'innerQuorumSets': []}, {'threshold': 2, 'validators': ['GABMKJM6I25XI4K7U6XWMULOUQIQ27BCTMLS6BYYSOWKTBUXVRJSXHYQ', 'GCGB2S2KGYARPVIA37HYZXVRM2YZUEXA6S33ZU5BUDC6THSB62LZSTYH', 'GCM6QMP3DLRPTAZW2UZPCPX2LF3SXWXKPMP3GKFZBDSF3QZGV2G5QSTK'], 'innerQuorumSets': []}, {'threshold': 2, 'validators': ['GADLA6BJK6VK33EM2IDQM37L5KGVCY5MSHSHVJA4SCNGNUIEOTCR6J5T', 'GAZ437J46SCFPZEDLVGDMKZPLFO77XJ4QVAURSJVRZK2T5S7XUFHXI2Z', 'GD6SZQV3WEJUH352NTVLKEV2JM2RH266VPEM7EH5QLLI7ZZAALMLNUVN'], 'innerQuorumSets': []}, {'threshold': 2, 'validators': ['GAK6Z5UVGUVSEK6PEOCAYJISTT5EJBB34PN3NOLEQG2SUKXRVV2F6HZY', 'GBJQUIXUO4XSNPAUT6ODLZUJRV2NPXYASKUBY4G5MYP3M47PCVI55MNT', 'GC5SXLNAM3C4NMGK2PXK4R34B5GNZ47FYQ24ZIBFDFOCU6D4KBN4POAE'], 'innerQuorumSets': []}, {'threshold': 2, 'validators': ['GARYGQ5F2IJEBCZJCBNPWNWVDOFK7IBOHLJKKSG2TMHDQKEEC6P4PE4V', 'GA7DV63PBUUWNUFAF4GAZVXU2OZMYRATDLKTC7VTCG7AU4XUPN5VRX4A', 'GCMSM2VFZGRPTZKPH5OABHGH4F3AVS6XTNJXDGCZ3MKCOSUBH3FL6DOB'], 'innerQuorumSets': []}, {'threshold': 3, 'validators': ['GA5STBMV6QDXFDGD62MEHLLHZTPDI77U3PFOD2SELU5RJDHQWBR5NNK7', 'GA7TEPCBDQKI7JQLQ34ZURRMK44DVYCIGVXQQWNSWAEQR6KB4FMCBT7J', 'GCB2VSADESRV2DDTIVTFLBDI562K6KE3KMKILBHUHUWFXCUBHGQDI7VL', 'GCFONE23AB7Y6C5YZOMKUKGETPIAJA4QOYLS5VNS4JHBGKRZCPYHDLW7', 'GD5QWEVV4GZZTQP46BRXV5CUMMMLP4JTGFD7FWYJJWRL54CELY6JGQ63'], 'innerQuorumSets': []}, {'threshold': 2, 'validators': ['GBLJNN3AVZZPG2FYAYTYQKECNWTQYYUUY2KVFN2OUKZKBULXIXBZ4FCT', 'GCIXVKNFPKWVMKJKVK2V4NK7D4TC6W3BUMXSIJ365QUAXWBRPPJXIR2Z', 'GCVJ4Z6TI6Z2SOGENSPXDQ2U4RKH3CNQKYUHNSSPYFPNWTLGS6EBH7I2'], 'innerQuorumSets': []}]}
        cur_node = {"publicKey": pk, "quorumSet": qs, "isValidator": True}
        res.append(cur_node)
    return res, all_fake_nodes

def _fetch_with_fake_nodes() -> list:
    """
    Get data from stellarbeat, filter out non-validator nodes, and return a list of dicts with two keys: 'publicKey' and 'quorumSet'.
    """
    url = "https://api.stellarbeat.io/v1/node"
    response = get(url, timeout=5)
    num_fake_nodes = 10
    fake_nodes, fake_pks = create_fake_nodes(num_fake_nodes)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if item['host'] != None and "satoshipay" in item['host']:
                traitor_qs = {"threshold":num_fake_nodes/2 + 1, "validators":fake_pks, "innerQuorumSets":[]}
                item['quorumSet'] = traitor_qs
        while len(fake_nodes) > 0:
            data.append(fake_nodes.pop())
        return [{'publicKey': node['publicKey'], 'quorumSet': node['quorumSet']}
            for node in data if node['isValidator']]
    else:
        response.raise_for_status()

def _fetch_with_fake_nodes_wPref() -> list:
    """
    Get data from stellarbeat, filter out non-validator nodes, and return a list of dicts with two keys: 'publicKey' and 'quorumSet'.
    """
    url = "https://api.stellarbeat.io/v1/node"
    response = get(url, timeout=5)
    num_fake_nodes = 10
    fake_nodes, fake_pks = create_fake_nodes(num_fake_nodes)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if item['host'] != None and "satoshipay" in item['host']:
                traitor_inner_qs = {"threshold":num_fake_nodes/2, "validators":fake_pks, "innerQuorumSets":[]}
                item['quorumSet']['innerQuorumSets'].append(traitor_inner_qs)
        while len(fake_nodes) > 0:
            data.append(fake_nodes.pop())
        return [{'publicKey': node['publicKey'], 'quorumSet': node['quorumSet']}
            for node in data if node['isValidator']]
    else:
        response.raise_for_status()

def get_validators(update=False) -> list:
    cache_dir = user_cache_dir('python-fbas', 'SDF', ensure_exists=True)
    path = os.path.join(cache_dir, 'validators.json')

    if update:
        print(f"Updating data at {path}")
        json_data = _fetch_from_url()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f)
    else:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            json_data = _fetch_from_url()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f)
    return json_data

def get_validators_from_file(path) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__=="__main__": 
    print(_fetch_from_url())