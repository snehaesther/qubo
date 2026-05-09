import numpy as np
import itertools
import matplotlib.pyplot as plt
import random



def build_Q(costs, edges, nodes, targets, P1=3, P2=2):
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
                        P_cost=1, P_flow=200, P_shared=80, P_degree=60):

    import numpy as np

    Q_blocks = []

    # -----------------------------
    # 1. Build single-path QUBO per path
    # -----------------------------
    for targets in targets_list:

        num_edges = len(edges)
        Q = np.zeros((num_edges, num_edges))

        # ---- Cost term (objective) ----
        for i in range(num_edges):
            Q[i, i] += P_cost * costs[i]

        # ---- FLOW CONSERVATION (MAIN FIX) ----
        for node in nodes:

            conn = []  # (edge_index, +1 or -1)

            for i, (u, v) in enumerate(edges):
                if u == node:
                    conn.append((i, +1))   # outgoing
                if v == node:
                    conn.append((i, -1))   # incoming

            target = targets[node]

            # Expand (sum s_i*x_i - target)^2
            for i, si in conn:
                Q[i, i] += P_flow * (si * si)
                Q[i, i] += -2 * P_flow * target * si

            for a in range(len(conn)):
                i, si = conn[a]
                for b in range(a + 1, len(conn)):
                    j, sj = conn[b]
                    Q[i, j] += 2 * P_flow * si * sj

        # ---- DEGREE CONSTRAINT (optional but useful) ----
        for node in nodes:

            outgoing = []
            incoming = []

            for i, (u, v) in enumerate(edges):
                if u == node:
                    outgoing.append(i)
                if v == node:
                    incoming.append(i)

            # Outgoing ≤ 1
            for i in outgoing:
                Q[i, i] += -P_degree
                for j in outgoing:
                    if i < j:
                        Q[i, j] += 2 * P_degree

            # Incoming ≤ 1
            for i in incoming:
                Q[i, i] += -P_degree
                for j in incoming:
                    if i < j:
                        Q[i, j] += 2 * P_degree

        Q_blocks.append(Q)

    # -----------------------------
    # 2. Combine paths (block diagonal)
    # -----------------------------
    n = Q_blocks[0].shape[0]
    num_paths = len(Q_blocks)

    Q_total = np.block([
        [Q_blocks[i] if i == j else np.zeros((n, n))
         for j in range(num_paths)]
        for i in range(num_paths)
    ])

    # -----------------------------
    # 3. Shared edge penalty
    # -----------------------------
    num_edges = len(edges)

    for e in range(num_edges):
        for p1 in range(num_paths):
            for p2 in range(p1 + 1, num_paths):

                i = p1 * n + e
                j = p2 * n + e

                Q_total[i, j] += P_shared
                Q_total[j, i] += P_shared

    return Q_total
def check_constraints(bits, edges, nodes, targets):

    flow = {n: 0 for n in nodes}

    for bit, (u, v) in zip(bits, edges):
        if bit == 1:
            flow[u] += 1
            flow[v] -= 1

    for n in nodes:
        if flow[n] != targets[n]:
            return False

    return True
def is_valid_path(selected_edges, targets):

    flow = {}

    for node in targets:
        flow[node] = 0

    for u, v in selected_edges:
        flow[u] += 1
        flow[v] -= 1

    for node in targets:
        if flow[node] != targets[node]:
            return False

    return True
def execute_qaoa_and_get_results(circuit, qpu, param_map, Q,nbshots):
    bitstrings = []
    probabilities = []

    final_circuit = circuit.bind_variables(param_map)
    final_job = final_circuit.to_job(nbshots=nbshots)
    final_result = qpu.submit(final_job)

    for sample in final_result:
        bitstring = sample.state.bitstring.zfill(Q.shape[0])
        bitstrings.append(bitstring)
        probabilities.append(sample.probability)

    return bitstrings, probabilities, final_result

def linear_ramp_parameters(depth,  delta_beta, delta_gamma):

    gammas = []
    betas = []

    for i in range(depth):
        gamma = ((i + 1) / depth) * delta_gamma
        beta = (1 - (i / depth)) * delta_beta
        gammas.append(gamma)
        betas.append(beta)

    param_map = {}

    for i in range(depth):
        param_map[f"\\gamma_{{{i}}}"] = gammas[i]
        param_map[f"\\beta_{{{i}}}"] = betas[i]

    return param_map
