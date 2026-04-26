import numpy as np
import itertools
import matplotlib.pyplot as plt
import random


def build_Q(costs, edges, nodes, targets, P1=20, P2=20):
    num_vars = len(costs) + (len(nodes) - 2)
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

        for i, s_vi in conn:
            Q[i, i] += P1 * (1 - 2 * Tv * s_vi)

            for j, s_vj in conn:
                if i < j:
                    Q[i, j] += 2 * P1 * s_vi * s_vj

    # Degree helper constraints
    helper_index = len(costs)

    for v in nodes:
        if targets[v] == 0:
            conn = []

            for i, (u, w) in enumerate(edges):
                if u == v or w == v:
                    conn.append(i)

            y_idx = helper_index
            helper_index += 1

            for i in conn:
                Q[i, i] += P2

                for j in conn:
                    if i < j:
                        Q[i, j] += 2 * P2

                Q[i, y_idx] -= 4 * P2

            Q[y_idx, y_idx] += 4 * P2

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
def build_multi_Q_strict(edges, path_targets, costs,
                         P_shared=10,
                         P_flow=20,
                         P_branch=15):

    import numpy as np

    num_edges = len(edges)
    num_paths = len(path_targets)

    total_variables = num_edges * num_paths
    Q = np.zeros((total_variables, total_variables))

    nodes = sorted(set(sum(edges, ())))

    for p in range(num_paths):
        for e in range(num_edges):
            idx = p * num_edges + e
            Q[idx, idx] += costs[e]

    for e in range(num_edges):
        for p1 in range(num_paths):
            for p2 in range(p1 + 1, num_paths):
                i = p1 * num_edges + e
                j = p2 * num_edges + e
                Q[i, j] += P_shared

    for p, (source, sink) in enumerate(path_targets):
        for e, (u, v) in enumerate(edges):
            idx = p * num_edges + e

            if u == source:
                Q[idx, idx] -= P_flow

            if v == sink:
                Q[idx, idx] -= P_flow

    for p in range(num_paths):
        for node in nodes:
            outgoing = [
                p * num_edges + e
                for e, (u, v) in enumerate(edges)
                if u == node
            ]

            for i in range(len(outgoing)):
                for j in range(i + 1, len(outgoing)):
                    Q[outgoing[i], outgoing[j]] += P_branch

    return Q