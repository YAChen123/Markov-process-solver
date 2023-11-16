# Markov-Process-Solver

## Run
type `make` in the terminal inside this repository to see all the outputs 


## Program
The program should take 4 flags and an input file

`-df` (Discount Factor):

This flag specifies a float value between 0 and 1 (inclusive) that represents the discount factor to be applied to future rewards. The discount factor determines the importance of future rewards compared to immediate rewards in the Markov decision process. A higher discount factor (closer to 1) gives more weight to future rewards, while a lower discount factor (closer to 0) gives less weight to future rewards. If this flag is not set, it defaults to 1.0, meaning there is no discounting of future rewards.

`-min` (Minimization Mode):

This flag is a boolean flag that determines whether the program should minimize values as costs or maximize values as rewards. If the flag is set to true, it indicates that the program should treat values as costs and aim to minimize them. If it's set to false or not specified, the program will assume values are rewards and aim to maximize them.

`-tol` (Tolerance):

This flag specifies a float value that represents the tolerance level for exiting the value iteration process. Value iteration is an iterative algorithm used to find the optimal values or policies in a Markov decision process. The program will continue iterating until the difference in values between consecutive iterations falls below this tolerance level. If not specified, it defaults to either 0.01 or 0.001, as mentioned, depending on the desired precision.

`-iter` (Iteration Cutoff):

This flag specifies an integer value that serves as a cutoff for the number of iterations in the value iteration process. Value iteration involves iteratively updating value estimates until convergence or reaching a maximum number of iterations. This flag sets the maximum number of iterations allowed. If not specified, it defaults to 100.

e.g.

`mdp -df .9 -tol 0.0001 some-input.txt`


## Algorithm
```   
    𝜋 = initial policy (arbitrary)
    V = initial values (perhaps using rewards)
    for {
      V = ValueIteration(𝜋) // computes V using stationery P
      𝜋' = GreedyPolicyComputation(V) // computes new P using latest V
      if 𝜋 == 𝜋' then return 𝜋, V
      𝜋 = 𝜋'
    }
```

1. Initialize 𝜋 (the policy) arbitrarily.

2. Initialize V (the value function) based on rewards or some initial values.

3. Enter a loop that continues until convergence is reached.

Inside the loop:

* Use the current policy 𝜋 to perform a Value Iteration step. ValueIteration computes a transition matrix using the fixed policy 𝜋 and iteratively updates the values for each state or node using the previous values until one of the stopping criteria is met:

  * No value changes by more than the 'tol' flag (convergence threshold).
  * The maximum number of iterations (-iter) is reached.
* After Value Iteration, you obtain an updated value function V.

* Use the updated value function V to perform Greedy Policy Computation. GreedyPolicyComputation calculates a new policy 𝜋' based on the current set of values. The nature of the policy (maximizing rewards or minimizing costs) depends on whether the '-min' flag is set:

  * If '-min' is not set (defaults to maximizing values as rewards), the policy is chosen to maximize rewards. This means that for each state, the action that leads to the highest expected reward is selected.
  * If '-min' is set, the policy is chosen to minimize costs. In this case, for each state, the action that leads to the lowest expected cost is selected.
* Check if the newly computed policy 𝜋' is the same as the previous policy 𝜋. If they are the same, it means that the policy has converged and is not changing significantly anymore. In this case, you can return the converged policy 𝜋 and the corresponding value function V as the optimal policy and values.

* If 𝜋 is not the same as 𝜋', update 𝜋 to be 𝜋' and continue the loop to perform another iteration.
  
## Bellman equation

The value of an individual state is computed using the Bellman equation for a Markov property

`v(s) = r(s) + df * P * v`

`v(s)`: This represents the value of the state s. In the context of an MDP, the value of a state indicates the expected cumulative reward (or cost, depending on whether you are maximizing or minimizing) that an agent can achieve when starting in state s and following a certain policy.

`r(s)`: This represents the reward or cost associated with being in state s. It's a fixed value that characterizes the immediate consequence or benefit of being in that state. For example, if you are modeling a game, r(s) might represent the immediate reward or penalty associated with being in a particular game state.

`df (Discount Factor)`: This is the discount factor, which is typically a value between 0 and 1. It's specified using the -df flag as you mentioned earlier. The discount factor determines how much importance is given to future rewards compared to immediate rewards. A higher discount factor values future rewards more, while a lower discount factor values immediate rewards more.

`P`: This represents the transition probability matrix. It describes the probabilities of transitioning from the current state s to other states under a given policy. The transition probabilities depend on both the current state and the chosen action. This matrix captures the dynamics of the MDP, indicating the likelihood of moving from one state to another.

## Input file and State types

The input file consists of 4 types of input lines:

* Comment lines that start with # and are ignored (as are blanklines)
* Rewards/costs lines of the form 'name = value' where value is an integer
* Edges of the form 'name : [e1, e2, e2]' where each e# is the name of an out edge from name
* Probabilities of the form 'name % p1 p2 p3'

eg.
```
    A = 7
    B % .9
    C : [ B, A]
    C=-1
    A : [B, A]
    A % .2 .8
    B : [A, C]
```

### Probability entries:
* A node with the same number of probabilities as edges is a chance node, with synchronized positions.

eg. 
```
 A : [ B, C, D]
 A % 0.1 0.2 0.7
```
Indicates that from node A there is a 10% chance of transitioning to node B, 20% to node C and 70% to node D.

* A node with a single probability 'name : p' is a decision node, with the given success rate.
As in the maze example, failures are split evenly amongst the other edges.

eg. 
```
 F : [C, E, G]
 F % .8
```
Given a policy of F -> E, transition probabilities would be {C=.1 E=.8 G=.1}, noting that this changes with the policy.

### Nodes
* If a node has edges but no probability entry, it is assumed to be a decision node with p=1
* If a node has edges but no reward entry, it is assumed to have a reward of 0
* If a node has no edges it is terminal. A probability entry for such a node is an error.
* If a node has a single edge it always transitions there. (this is useful for capturing some reward on the way)
* A node referenced as an edge must separately have one of the three entries to be valid
* Therefore to create a 0 value terminal node you must do 'name = 0'


## Refernece
This code is based on, and has been modified from, the MDP Solver found at [Markov Process Solver](https://github.com/TestSubjector/NYU_CSCI_GA_2560/tree/master/Lab3) by [Kumar Prasun](https://github.com/TestSubjector).