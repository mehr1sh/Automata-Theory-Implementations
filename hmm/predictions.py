import sys
import os
from collections import defaultdict

# function to parse dataset to build hmm matrices from scratch
def load_hmm(dataset_path):
    with open(dataset_path,"r") as f:
        lines = f.readlines()

    n_runs = int(lines[0].strip())

    trans_counts = defaultdict(lambda: defaultdict(int))
    emiss_counts = defaultdict(lambda: defaultdict(int))
    state_counts = defaultdict(int)

    states_set = set()
    obs_set = set()

    idx = 1
    for _ in range(n_runs):
        states_seq = list(map(int, lines[idx].strip().split()))
        idx += 1
        obs_seq = list(map(int, lines[idx].strip().split()))
        idx += 1

        for i in range(len(states_seq)-1):
            trans_counts[states_seq[i]][states_seq[i+1]] += 1

        for s, o in zip(states_seq, obs_seq):
            emiss_counts[s][o] += 1
            state_counts[s] +=1

        states_set.update(states_seq)
        obs_set.update(obs_seq)

    states = sorted(states_set)
    obs = sorted(obs_set)

    N, M = len(states), len(obs)
    st_idx = {s:i for i, s in enumerate(states)}
    ob_idx = {o:i for i, o in enumerate(obs)}

    # initialize matrices with zeros
    A = [[0.0]*N for _ in range(N)]
    B = [[0.0]*M for _ in range(N)]

    # build transition matrix with probabilities
    for from_st in states:
        total_transitions = sum(trans_counts[from_st][to_st] for to_st in states)
        i = st_idx[from_st]
        for to_st in states:
            j = st_idx[to_st]
            A[i][j] = (trans_counts[from_st][to_st]/total_transitions) if total_transitions>0 else 0.0

    # build emission matrix similarly
    for st in states:
        total_emissions = state_counts[st]
        i = st_idx[st]
        for o in obs:
            j = ob_idx[o]
            B[i][j] = (emiss_counts[st][o]/total_emissions) if total_emissions>0 else 0.0

    return states, obs, A, B, st_idx, ob_idx

# viterbi algorithm to calculate most probable hidden states sequence given observations
def viterbi(obs_seq, states, obs, A, B, st_idx, ob_idx):
    T = len(obs_seq)
    N = len(states)
    start_state = 0

    obs_ids = [ob_idx[o] for o in obs_seq]

    dp = [{} for _ in range(T)]

    # initialize dp for first observation
    for s in states:
        if s != start_state:
            prev_i = st_idx[start_state]
            curr_i = st_idx[s]
            dp[0][s] = (A[prev_i][curr_i]*B[curr_i][obs_ids[0]], start_state)

    # compute maximum probabilities for each time step
    for t in range(1, T):
        for curr_s in states:
            if curr_s == start_state:
                continue
            curr_i = st_idx[curr_s]
            max_prob = -1.0
            prev_state_chosen = None
            for prev_s in states:
                if prev_s == start_state:
                    continue
                prev_i = st_idx[prev_s]
                prob = dp[t-1][prev_s][0] * A[prev_i][curr_i] * B[curr_i][obs_ids[t]]
                if prob > max_prob:
                    max_prob = prob
                    prev_state_chosen = prev_s

            dp[t][curr_s] = (max_prob, prev_state_chosen)

    # backtrack to extract states path
    last_time_states = dp[-1]
    final_state = max(last_time_states, key=lambda s: last_time_states[s][0])

    path = [final_state]
    for t in range(T-1, 0, -1):
        state = dp[t][path[-1]][1]
        path.append(state)

    path.reverse()
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage : python predictions.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file,"r") as f:
        lines = [line.strip() for line in f if line.strip()]

    dataset_file = lines[0]

    states, obs, A, B, st_idx, ob_idx = load_hmm(dataset_file)

    idx = 1
    total_tests = int(lines[idx])
    idx += 1

    results = []

    for _ in range(total_tests):
        L = int(lines[idx])
        idx += 1
        observation_sequence = list(map(int, lines[idx].split()))
        idx += 1

        best_path = viterbi(observation_sequence, states, obs, A, B, st_idx, ob_idx)
        results.append(" ".join(map(str, best_path)) + "\n")

    output_path = os.path.splitext(input_file)[0] + "_output.txt"
    with open(output_path, "w") as out:
        out.writelines(results)
