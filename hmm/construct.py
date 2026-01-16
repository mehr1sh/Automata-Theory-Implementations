import sys
import os
from collections import defaultdict

# starting point to build hmm matrices from input dataset file
if len(sys.argv) != 2:
    print("usage : python construct.py <dataset_file>")
    sys.exit(1)

dataset_file = sys.argv[1]

with open(dataset_file, "r") as file:
    lines = file.readlines()

# get how many data points runs in dataset
total_runs = int(lines[0].strip())

# dictionaries to count transitions and emissions frequencies
transition_counts = defaultdict(lambda: defaultdict(int))
emission_counts = defaultdict(lambda: defaultdict(int))
state_appearance_counts = defaultdict(int)

all_states = set()
all_observables = set()

index = 1
for _ in range(total_runs):
    # read states and observations for this run
    states_list = list(map(int, lines[index].strip().split()))
    index += 1
    observables_list = list(map(int, lines[index].strip().split()))
    index += 1

    # count how many times we move between states in this run
    for i in range(len(states_list) - 1):
        curr_state = states_list[i]
        next_state = states_list[i + 1]
        transition_counts[curr_state][next_state] += 1

    # count how many times each observable was emitted in a state
    for s, o in zip(states_list, observables_list):
        emission_counts[s][o] += 1
        state_appearance_counts[s] += 1

    # keep track of all states and observables seen so far
    all_states.update(states_list)
    all_observables.update(observables_list)

# sort states and observables to have consistent matrix order
sorted_states = sorted(all_states)
sorted_observables = sorted(all_observables)

num_states = len(sorted_states)
num_obs = len(sorted_observables)

# mapping from actual state/obs to their indices in matrix rows/columns
state_to_idx = {s:i for i, s in enumerate(sorted_states)}
obs_to_idx = {o:i for i, o in enumerate(sorted_observables)}

# initialize matrices empty
trans_matrix = [[0.0]*num_states for _ in range(num_states)]
emiss_matrix = [[0.0]*num_obs for _ in range(num_states)]

# calculate transition probability matrix A using frequency counts
for from_state in sorted_states:
    total_outgoing = sum(transition_counts[from_state][to_s] for to_s in sorted_states)
    i = state_to_idx[from_state]
    for to_state in sorted_states:
        j = state_to_idx[to_state]
        if total_outgoing > 0:
            trans_matrix[i][j] = transition_counts[from_state][to_state]/total_outgoing
        else:
            trans_matrix[i][j] = 0.0

# calculate emission probability matrix B using frequency counts
for state in sorted_states:
    total_emissions = state_appearance_counts[state]
    i = state_to_idx[state]
    for obs in sorted_observables:
        j = obs_to_idx[obs]
        if total_emissions > 0:
            emiss_matrix[i][j] = emission_counts[state][obs]/total_emissions
        else:
            emiss_matrix[i][j] = 0.0

# prepare output matrices as strings (numbers rounded to 5 decimals)
output_lines = []
for row in trans_matrix:
    output_lines.append(" ".join(map(lambda x: f"{x:.5f}", row)) + "\n")
for row in emiss_matrix:
    output_lines.append(" ".join(map(lambda x: f"{x:.5f}", row)) + "\n")

output_path = os.path.splitext(dataset_file)[0] + "_output.txt"
with open(output_path,"w") as outfile:
    outfile.writelines(output_lines)
