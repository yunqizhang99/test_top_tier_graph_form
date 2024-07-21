Both algs assume that (1) we know the set of validators in the graph, and (2) all validators in the graph are honest.

alg1: Validators try to satisfy their own quorumsets and do not accept new connections once their quorumsets are satisfied. However, if the graph doesn't converge within time t, validators start accepting an extra connection. This repeats until the graph converges. 

alg2: Validators try to satisfy their own quorumsets but also accept connections even if their quorumsets are satisfied. The graph converges quickly, and then the validators try pruning connections one edge at a time (how?).
