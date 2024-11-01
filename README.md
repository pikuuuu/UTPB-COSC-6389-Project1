# UTPB-COSC-6389-Project1
This repo contains the assignment and code base for Project 1 of the graduate Computational Biomimicry class.

The goals of this project are:
1) Improve student understanding of Python
2) Understand UI programming considerations
3) Understand how to represent several hard problems with simple data structures
4) Gain experience with several optimization techniques, and how to select techniques which will work best on a given problem

Description:
The provided Python code base contains the following:
1) An implementation of a Knapsack solver using a rudimentary genetic algorithm approach which correctly displays the problem and the best potential solution in the UI in real time, but is very poorly optimized.
2) An implementation of a Traveling Salesman network generator which displays the network, but does not provide any meaningful mechanism for solving the TSP and will not currently be capable of properly displaying candidate solutions in real time.
3) A series of code snippets which provide examples of the Hill Climbing, Simulated Annealing, and Tabu Search algorithms, along with all of the selection, crossover, and mutation strategies we covered in class.
Your goal is to accomplish three things, and I would recommend you tackle them in order.

First, modify the Knapsack solver to make use of a better tactic for solving the problem.  The existing solution uses a fitness function which tends to heavily bias the population toward specific solutions.  The use of the roulette wheel selection system reinforces this bias.  The crossover and mutation methods in use are single-point crossover, and single-point binary flip mutation.  Both of these tend to fail to produce the level of diversity in the population that we need to efficiently find solutions.  Experiment with the other techniques at your disposal and implement the one you believe is most effective.

Second, modify the TSP code to both allow it to efficiently arrive at a high-quality solution to the problem, and display its current best solution in real time, by modifying the colors/fill of the displayed network elements to differentiate those which are included in the current solution from those which are not.  Again, your goal here is to try to find the most efficient method you can to solve TSP using the tools available to you.

Third, select one additional problem from https://en.wikipedia.org/wiki/List_of_NP-complete_problems (not including TSP or Knapsack), and create a complete generation/display/solver application for that problem.

Fourth, create an implementation of one of the swarm-based optimization techniques we discussed in class (particle swarms or ant-colony optimization) and include it as an optional solver for either your TSP or your extra problem.

Grading criteria:
1) If the code submitted via your pull request does not compile, the grade is zero.
2) If the code crashes due to forseeable unhandled exceptions, the grade is zero.
3) For full points, the code must correctly perform the relevant algorithms and display the intermediate steps in real time, via the UI.

Deliverables for this project:
Three Python files, one containing the implementation of the Knapsack application, another for the TSP application, and a third for the user's choice problem application.

