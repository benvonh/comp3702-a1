from os import environ
import sys
import heapq as hq
from constants import *
from environment import *
from state import State

"""
solution.py

This file is a template you should use to implement your solution.

You should implement 

COMP3702 2022 Assignment 1 Support Code

Last updated by njc 01/08/22
"""


class Solver:

    def __init__(self, environment, loop_counter):
        self.environment = environment
        self.loop_counter = loop_counter
        self._queue = [] # array of (running_cost, [action_history], new_state) tuple
        self._visited_states = set()


    def solve_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        state = self.environment.get_init_state()
        self._visited_states.add(state)
        self.expand_node(0, [], state)
        self.loop_counter.inc()

        while not self.environment.is_solved(state):
            lowest_cost_action = hq.heappop(self._queue)
            self.expand_node(*lowest_cost_action)
            state = lowest_cost_action[2]
            self.loop_counter.inc()

        return lowest_cost_action[1]


    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        pass


    def expand_node(self, running_cost: float, action_history: list, prev_state: State):
        """
        """
        for action in ROBOT_ACTIONS:
            success, cost, state = self.environment.perform_action(prev_state, action)
            if success and state not in self._visited_states:
                history = action_history.copy()
                history.append(action)
                self._queue.append((cost + running_cost, history, state))
                self._visited_states.add(state)
