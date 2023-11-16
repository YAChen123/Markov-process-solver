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
        elif len(self.probabilities) == 1 or (len(self.transitions) > 0 and not self.probabilities):
            self.decision = True
            if not self.probabilities:
                self.probabilities.append(1)
        elif not self.transitions:
            self.terminal = True  

def parse_states(args):
    # parse the input
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

    return state_dict

def process_states(state_dict):
    for state in state_dict.values():
        state.determine_type()

def bellman_equation(target_state, state_dict, discount_factor):
    # Check if the target state represents a chance node
    if target_state.chance:
        # Calculate the expected value for a chance node
        expected_value = sum(
            probability * state_dict[transition].value
            for probability, transition in zip(target_state.probabilities, target_state.transitions)
        )
    # Check if the target state represents a decision node
    elif target_state.decision:
        # Calculate the value for a decision node based on the policy
        main_probability = target_state.probabilities[0]
        num_transitions = len(target_state.transitions)
        
        if num_transitions == 1:
            remaining_probability = 0
        else:
            remaining_probability = (1 - main_probability) / (num_transitions - 1)
        
        chosen_transition = target_state.policy
        expected_value = sum(
            (main_probability if transition == chosen_transition else remaining_probability)
            * state_dict[transition].value
            for transition in target_state.transitions
        )
    else:
        # The target state does not affect the score
        expected_value = 0

    # Calculate the Bellman value using the reward and expected value
    bellman_value = target_state.reward + discount_factor * expected_value

    return bellman_value

def calculate_policy(target_state, state_dict, minimize):
    # Extract main probability and calculate remaining probability
    main_probability = target_state.probabilities[0]
    remaining_probability = 0
    num_transitions = len(target_state.transitions)

    if num_transitions != 1:
        remaining_probability = (1 - main_probability) / (num_transitions - 1)
        
    current_value = target_state.value
    best_policy = None

    # Iterate over each possible policy

    for _, main_transition in enumerate(target_state.transitions):
        total_sum = 0

        # Calculate the expected value for each policy
        for side_transition in target_state.transitions:
            if main_transition == side_transition:
                total_sum += main_probability * state_dict[side_transition].value
            else:
                total_sum += remaining_probability * state_dict[side_transition].value

        # Update the best policy based on minimizing or maximizing        
        if minimize:
            if total_sum < current_value:
                target_state.policy = main_transition
                current_value = total_sum
        else:
            if total_sum > current_value:
                target_state.policy = main_transition
                current_value = total_sum
    
    # Set the target state's policy to the best policy found
    best_policy = target_state.policy

    return best_policy

def solve_markov_decision_process(state_dict, discount_factor, minimize, tolerance, iterations):
    # Initialize policies for non-terminal states
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

def print_result(state_dict):
    for state in state_dict.values():
        if state.decision and len(state.transitions) > 1:
            print(f"{state.name} -> {state.policy}")
    print()
    for state in state_dict.values():
        rounded_value = round(state.value, 3)  # Round to 3 decimal places
        print(f"{state.name} = {rounded_value}", end=" ")
    print()
     
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-df", "--df", type=float, default=1.0, help="A float argument")
    parser.add_argument("-min", "--min", action='store_true', help="Enable the minimize option")
    parser.add_argument("-tol", "--tol", type=float, default=0.01, help="Tolerance level")
    parser.add_argument("-iter", "--iter", type=int, default=100, help="Number of iterations")
    parser.add_argument("-i", "--input", default=None, help="Input file name")
    args = parser.parse_args()

    # parse the state from the input file
    state_dict = parse_states(args)

    # determine the state type
    process_states(state_dict)

    # markov decision solver
    solve_markov_decision_process(state_dict, args.df, args.min, args.tol, args.iter)
    
    # print the result
    print_result(state_dict)

if __name__ == "__main__":
    main()
