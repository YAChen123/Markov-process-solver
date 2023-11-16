import argparse

# Define a class to represent the states in the Markov Decision Process
class State:
    def __init__(self, name):
        self.name = name
        self.chance = False
        self.decision = False
        self.terminal = False
        self.reward = 0
        self.transitions = []
        self.probabilities = []
        self.value = 0
        self.policy = name

    def determine_type(self):
        if len(self.transitions) == len(self.probabilities) > 0:
            self.chance = True
        elif len(self.probabilities) == 1:
            self.decision = True
        elif len(self.transitions) > 0:
            self.decision = True
            self.probabilities.append(1)
        elif len(self.probabilities) == 1:
            self.decision = True
        elif not self.transitions:
            self.terminal = True    
        
        if self.chance and sum(self.probabilities) != 1:
            print(f"Error: Sum of probabilities is not 1 for chance state {self.name}")
            exit(0)

    def print_policy(self):
        print(f"{self.name} -> {self.policy}")

def parse_states(args):
    with open(args.input, "r") as input_file:
        graph_data = input_file.read()

    state_dict = {}
    lines = graph_data.split("\n")
    for line in lines:
        line = line.replace("=", " = ").replace(":", " : ").replace("%", " % ")
        line = line.replace("[", " [ ").replace("]", " ] ").replace(",", " ")
        parts = line.strip().split()
        if not parts or parts[0].startswith("#"):
            continue

        name = parts[0]
        if name not in state_dict:
            state_dict[name] = State(name)
        
        current_state = state_dict[name]
        
        if parts[1] == "=":
            current_state.reward = float(parts[2])
        elif parts[1] == "%":
            current_state.probabilities.extend(map(float, parts[2:]))
        elif parts[1] == ":":
            current_state.transitions.extend(parts[3:-1])
        else:
            print(f"{parts[1]} is in an unsupported format")

    return state_dict

def process_states(state_dict):
    for state in state_dict.values():
        state.determine_type()

def bellman_equation(target_state, state_dict, discount_factor):
    if target_state.chance:
        score = sum(target_state.probabilities[count] * state_dict[transition].value
                    for count, transition in enumerate(target_state.transitions))
    elif target_state.decision:
        main_prob = target_state.probabilities[0]
        rem_prob = (1 - main_prob) / (len(target_state.transitions) - 1) if len(target_state.transitions) != 1 else 0
        policy = target_state.policy
        score = sum(main_prob * state_dict[transition].value if transition == policy
                    else rem_prob * state_dict[transition].value
                    for transition in target_state.transitions)
    else:
        score = 0

    return target_state.reward + discount_factor * score

def calculate_policy(target_state, state_dict, minimize):
    main_prob = target_state.probabilities[0]
    rem_prob = 0
    if len(target_state.transitions) != 1:
        rem_prob = (1 - main_prob) / (len(target_state.transitions) - 1)
    current_value = target_state.value
    for _, main_transition in enumerate(target_state.transitions):
        total_sum = 0
        for side_transition in target_state.transitions:
            if main_transition == side_transition:
                total_sum += main_prob * state_dict[side_transition].value
            else:
                total_sum += rem_prob * state_dict[side_transition].value
        if minimize:
            if total_sum < current_value:
                target_state.policy = main_transition
                current_value = total_sum
        elif total_sum > current_value:
            target_state.policy = main_transition
            current_value = total_sum
    return target_state.policy

def solve_markov_decision_process(state_dict, discount_factor, minimize, tolerance, iterations):
    for state in state_dict.values():
        if not state.terminal:
            state.policy = state.transitions[0]

    while True:
        # Value Iteration Loop
        for _ in range(iterations):
            value_changed = False
            for state in state_dict.values():
                new_value = bellman_equation(state, state_dict, discount_factor)
                if abs(new_value - state.value) > tolerance:
                    value_changed = True
                state.value = new_value
            if not value_changed:
                break

        # Policy Iteration Loop
        policy_changed = False
        for state in state_dict.values():
            if state.decision:
                old_policy = state.policy 
                new_policy = calculate_policy(state, state_dict, minimize)
                if old_policy != new_policy:
                    policy_changed = True
                state.policy = new_policy
        if not policy_changed:
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-df", const=str, nargs="?", type=float, default=1.0)
    parser.add_argument("-min", action='store_true', default=False)
    parser.add_argument("-tol", const=str, nargs="?", type=float, default=0.01)
    parser.add_argument("-iter", const=str, nargs="?", type=int, default=100)
    parser.add_argument("-i", "--input", const=str, nargs="?", default=None)
    args = parser.parse_args()

    if args.df > 1 or args.df < 0:
        print("Discount factor argument not in [0, 1]. Terminating the program.")
        exit(0)

    state_dict = parse_states(args)
    process_states(state_dict)

    solve_markov_decision_process(state_dict, args.df, args.min, args.tol, args.iter)
    
    for state in state_dict.values():
        if state.decision and len(state.transitions) > 1:
            state.print_policy()
    print()
    for state in state_dict.values():
        rounded_value = round(state.value, 3)  # Round to 3 decimal places
        print(f"{state.name} = {rounded_value}", end=" ")
    print()

if __name__ == "__main__":
    main()
