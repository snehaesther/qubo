import numpy as np
import json

def build_qubo_matrix(json_file, penalty=5):

    with open(json_file) as f:
        data = json.load(f)

    ducts = data["ducts"]
    edges = list(ducts.keys())
    cost = {edge: ducts[edge] for edge in edges}

    nodes = data["nodes"]

    # starting node
    source = data["required_connections"][0][0]

    # ending node
    target = data["required_connections"][0][1]

    # flow constraints
    T = {node: 0 for node in nodes}

    T[source] = 1
    T[target] = -1

   # stores direction of edges connected to each node
    edge_direction = {}

    for edge in edges:

        node1, node2 = eval(edge)

        edge_direction[(node1, edge)] = 1
        edge_direction[(node2, edge)] = -1

    n = len(edges)

    # create empty matrix
    Q = np.zeros((n, n))

    # cost term
    for i, e in enumerate(edges):

        Q[i, i] += cost[e]

    # constraint term
    for node in nodes:

        connected_edges = []
        for e in edges:
            if (node, e) in edge_direction:
                connected_edges.append(e)

        for edge1 in connected_edges:
            for edge2 in connected_edges:

                i = edges.index(edge1)

                j = edges.index(edge2)

                Q[i, j] += penalty * edge_direction[(node, edge1)] * edge_direction[(node, edge2)]


        for e in connected_edges:

            i = edges.index(e)

            Q[i, i] += -2 * penalty * T[node] * edge_direction[(node, e)]


    return Q, edges