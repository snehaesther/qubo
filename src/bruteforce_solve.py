import numpy as np
import itertools

def brute_force_solve(Q):

    best_solution = None
    lowest_energy = float("inf")

    # generate all possible binary solutions 
    for binary_solution in itertools.product([0,1], repeat=len(Q)):

        x = np.array(binary_solution)

        # compute energy using QUBO formula x^T Q x
        energy = x @ Q @ x

        if energy < lowest_energy:

            lowest_energy = energy
            best_solution = binary_solution

    return best_solution, lowest_energy
