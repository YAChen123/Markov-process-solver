import java.io.*;
import java.util.*;

public class MarkovDecisionProcess {

    static class State {
        String name;
        double reward;
        Map<State, Double> transitions;

        public State(String name) {
            this.name = name;
            this.transitions = new HashMap<>();
            this.reward = 0.0; // Default reward, modify as necessary
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append("State: ").append(name).append(", Reward: ").append(reward).append(", Transitions: {");
            transitions.forEach((state, probability) -> sb.append(" [").append(state.name).append(" -> ").append(probability).append("]"));
            sb.append(" }");
            return sb.toString();
        }

        // Add methods for adding transitions, setting reward, etc.
    }

    private Map<String, State> states;
    private double tolerance;
    private int maxIterations;
    private double discountFactor;
    private Map<State, State> policy; // A map to hold the optimal policy for each state


    public MarkovDecisionProcess(double tolerance, int maxIterations, double discountFactor) {
        this.states = new HashMap<>();
        this.tolerance = tolerance;
        this.maxIterations = maxIterations;
        this.discountFactor = discountFactor;
        this.policy = new HashMap<>();
    }

    public void printStates() {
        for (State state : states.values()) {
            System.out.println(state);
        }
    }

    public void printStateValues() {
        for (State state : states.values()) {
            System.out.println("State: " + state.name + ", Value: " + state.reward);
        }
    }
    
    
    public void parseInput(String filename) {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = reader.readLine()) != null) {
                // Skip comments and empty lines
                if (line.startsWith("#") || line.trim().isEmpty()) {
                    continue;
                }
    
                // Handle reward/cost lines
                if (line.contains("=")) {
                    String[] parts = line.split("=");
                    String stateName = parts[0].trim();
                    double reward = Double.parseDouble(parts[1].trim());
                    states.computeIfAbsent(stateName, State::new).reward = reward;
                }
                // Handle edge lines
                else if (line.contains(":")) {
                    String[] parts = line.split(":");
                    String stateName = parts[0].trim();
                    String[] edges = parts[1].trim().replaceAll("[\\[\\]]", "").split(",");
                    State state = states.computeIfAbsent(stateName, State::new);
                    for (String edge : edges) {
                        edge = edge.trim();
                        state.transitions.put(states.computeIfAbsent(edge, State::new), 0.0); // Initial probability set to 0.0
                    }
                }
                // Handle probability lines
                else if (line.contains("%")) {
                    String[] parts = line.split("%");
                    String stateName = parts[0].trim();
                    String[] probabilities = parts[1].trim().split(" ");
                    State state = states.get(stateName);
    
                    if (probabilities.length == 1) {
                        // Decision node with success rate
                        double successRate = Double.parseDouble(probabilities[0]);
                        double failureRate = (1 - successRate) / (state.transitions.size() - 1);
                        for (State target : state.transitions.keySet()) {
                            state.transitions.put(target, failureRate);
                        }
                        // Assuming the policy decision is the first edge (this may need to be adjusted based on actual policy)
                        State firstEdge = state.transitions.keySet().iterator().next();
                        state.transitions.put(firstEdge, successRate);
                    } else {
                        // Chance node
                        int index = 0;
                        for (State target : state.transitions.keySet()) {
                            double probability = Double.parseDouble(probabilities[index++].trim());
                            state.transitions.put(target, probability);
                        }
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    

    public void valueIteration() {
        boolean isConverged;
        Map<State, Double> stateValues = new HashMap<>(); // Map to store state values
    
        // Initialize state values to 0 (or to their immediate rewards if you prefer)
        // Initialize state values to a small value instead of 0.0
        for (State s : states.values()) {
            stateValues.put(s, s.reward != 0.0 ? s.reward : 0.1); // or some other small value
        }

    
        for (int iteration = 0; iteration < maxIterations; iteration++) {
            System.out.println("iteration number: " + iteration);
            isConverged = true;
            Map<State, Double> newStateValues = new HashMap<>(); // Temporary map for new values
    
            for (State currentState : states.values()) {
                if (currentState.transitions.isEmpty()) {
                    newStateValues.put(currentState, currentState.reward); // Keep value for terminal states
                    continue;
                }
                
                double newValue = Double.NEGATIVE_INFINITY;

                System.out.println("State: " + currentState.name + ", New Value: " + newValue + ", Old Value: " + stateValues.get(currentState));

    
                for (Map.Entry<State, Double> transition : currentState.transitions.entrySet()) {
                    State nextState = transition.getKey();
                    double transitionProbability = transition.getValue();
                    double nextStateValue = stateValues.get(nextState);
    
                    double tempValue = currentState.reward + discountFactor * transitionProbability * nextStateValue;
    
                    newValue = Math.max(newValue, tempValue);
                }
    
                newStateValues.put(currentState, newValue);
    
                // Check for convergence
                if (Math.abs(newValue - stateValues.get(currentState)) > tolerance) {
                    isConverged = false;
                }
            }
    
            stateValues = newStateValues; // Update the state values
    
            if (isConverged) {
                break;
            }
        }
    
        // Update state rewards with computed values for printing (optional)
        for (State s : states.values()) {
            s.reward = stateValues.get(s);
        }
    }
    
    

    public void determinePolicy() {
        for (State currentState : states.values()) {
            if (currentState.transitions.isEmpty()) {
                // Terminal state, no policy needed
                continue;
            }

            State bestNextState = null;
            double bestValue = Double.NEGATIVE_INFINITY;

            for (State nextState : currentState.transitions.keySet()) {
                double nextStateValue = states.get(nextState.name).reward; // Get the value of the next state

                if (nextStateValue > bestValue) {
                    bestValue = nextStateValue;
                    bestNextState = nextState;
                }
            }

            // Set the best next state in the policy map
            policy.put(currentState, bestNextState);
        }
    }


    public void printResults() {
        for (Map.Entry<State, State> entry : policy.entrySet()) {
            String currentStateName = entry.getKey().name;
            String bestNextStateName = entry.getValue() != null ? entry.getValue().name : "None";
            System.out.println(currentStateName + " -> " + bestNextStateName + " ");
        }
        System.out.println();

        for (State state : states.values()) {
            System.out.print(state.name + "=" + String.format("%.3f", state.reward) + " ");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        double discountFactor = 1.0; // Default value
        boolean minimize = false;    // Default value
        double tolerance = 0.01;     // Default value
        int maxIterations = 100;     // Default value
        String filename = null;

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "-df":
                    if (i + 1 < args.length) {
                        discountFactor = Double.parseDouble(args[++i]);
                    }
                    break;
                case "-min":
                    minimize = true;
                    break;
                case "-tol":
                    if (i + 1 < args.length) {
                        tolerance = Double.parseDouble(args[++i]);
                    }
                    break;
                case "-iter":
                    if (i + 1 < args.length) {
                        maxIterations = Integer.parseInt(args[++i]);
                    }
                    break;
                default:
                    filename = args[i]; // Assuming the filename is the last argument
                    break;
            }
        }
    
        if (filename == null) {
            System.out.println("No input file specified.");
            return;
        }
        System.out.println("maxIterations: " + discountFactor);
        System.out.println("tolerance: " + tolerance);
        System.out.println("maxIterations: " + maxIterations);
        System.out.println("filename: " + filename);

        MarkovDecisionProcess mdp = new MarkovDecisionProcess(tolerance, maxIterations, discountFactor);
        mdp.parseInput(filename);
        mdp.printStates();
        mdp.valueIteration();
        mdp.printStateValues();
        mdp.determinePolicy();
        mdp.printResults();
    }
}
