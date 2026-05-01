import numpy as np
import itertools
import matplotlib.pyplot as plt
import random


def build_Q(costs, edges, nodes, targets, P1=200, P2=50):
    num_vars = len(costs)   # ← IMPORTANT CHANGE
    Q = np.zeros((num_vars, num_vars))

    # Linear edge costs
    for i in range(len(costs)):
        Q[i, i] += costs[i]

    # Flow constraints
    for v in nodes:
        conn = []

        for i, (u, w) in enumerate(edges):
            if u == v:
                conn.append((i, 1))
            elif w == v:
                conn.append((i, -1))

        Tv = targets[v]

        # Diagonal
        for i, s_vi in conn:
            Q[i, i] += P1 * (s_vi * s_vi)
            Q[i, i] += -2 * P1 * Tv * s_vi

        # Off-diagonal
        for idx1 in range(len(conn)):
            i, s_vi = conn[idx1]
            for idx2 in range(idx1 + 1, len(conn)):
                j, s_vj = conn[idx2]
                Q[i, j] += 2 * P1 * s_vi * s_vj

    return Q

def check_validity(bits, edges, nodes, targets):
    active_edges = [edges[i] for i in range(len(edges)) if bits[i] == 1]

    if not active_edges:
        return False

    for v in nodes:
        in_degree = sum(1 for u, w in active_edges if w == v)
        out_degree = sum(1 for u, w in active_edges if u == v)

        if (out_degree - in_degree) != targets[v]:
            return False

    return True


def get_path_string(bits, edge_names):
    chosen = [
        edge_names[i]
        for i in range(len(edge_names))
        if bits[i] == 1
    ]

    return " -> ".join(chosen) if chosen else "No Path"


def brute_force(Q, costs, edges, nodes, targets):
    num_vars = Q.shape[0]

    valid_results = []

    for bits in itertools.product([0, 1], repeat=num_vars):
        x = np.array(bits)

        energy = x.T @ Q @ x

        if check_validity(bits, edges, nodes, targets):
            path_cost = sum(
                costs[i]
                for i in range(len(edges))
                if bits[i] == 1
            )

            valid_results.append({
                "bits": bits,
                "energy": energy,
                "path_cost": path_cost
            })

    best = min(valid_results, key=lambda r: r["energy"])

    return best


def classical_shortest_path(costs):
    candidates = [
        costs[0] + costs[3],
        costs[1] + costs[4],
        costs[0] + costs[2] + costs[4]
    ]

    return min(candidates)


def test_run():
    edges = [(0,1), (0,2), (1,2), (1,3), (2,3)]
    edge_names = ["AB","AC","BC","BD","CD"]
    nodes = [0,1,2,3]
    targets = {0:1,1:0,2:0,3:-1}

    costs = [random.randint(1,9) for _ in range(5)]

    Q = build_Q(costs, edges, nodes, targets)

    best = brute_force(Q, costs, edges, nodes, targets)

    qubo_cost = best["path_cost"]
    classical_cost = classical_shortest_path(costs)

    status = "PASS" if qubo_cost == classical_cost else "FAIL"

    print("Costs:", costs)
    print("QUBO Cost:", qubo_cost)
    print("Classical Cost:", classical_cost)
    print("Result:", status)
def build_multi_Q_strict(costs, edges, nodes, targets_list,
                        P1=200, P2=50, P_shared=100):

    import numpy as np

    Q_blocks = []

    for targets in targets_list:
        Q_blocks.append(build_Q(costs, edges, nodes, targets, P1, P2))

    n = Q_blocks[0].shape[0]
    num_paths = len(Q_blocks)

    Q_total = np.block([
        [Q_blocks[i] if i == j else np.zeros((n, n))
         for j in range(num_paths)]
        for i in range(num_paths)
    ])

    # Shared edge penalty
    num_edges = len(edges)

    for e in range(num_edges):
        for p1 in range(num_paths):
            for p2 in range(p1 + 1, num_paths):

                i = p1 * n + e
                j = p2 * n + e

                Q_total[i, j] += P_shared
                Q_total[j, i] += P_shared

    # ✅ NOW ADD DEGREE CONSTRAINT HERE (same indentation as above loop)
    P_degree = 100

    for p in range(num_paths):
        for node in nodes:

            outgoing = []
            incoming = []

            for e, (u, v) in enumerate(edges):
                idx = p * n + e

                if u == node:
                    outgoing.append(idx)

                if v == node:
                    incoming.append(idx)

            # OUTGOING ≤ 1
            for i in outgoing:
                Q_total[i, i] += -P_degree
                for j in outgoing:
                    if i < j:
                        Q_total[i, j] += 2 * P_degree

            # INCOMING ≤ 1
            for i in incoming:
                Q_total[i, i] += -P_degree
                for j in incoming:
                    if i < j:
                        Q_total[i, j] += 2 * P_degree

    
    return Q_total