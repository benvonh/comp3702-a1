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
        self._visited_states = {}


    def solve_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        self._visited_states = { self.environment.get_init_state(): 0 }
        lowest_cost_action = (0, 0, self.environment.get_init_state())
        self.expand_node(0, [], self.environment.get_init_state())

        while not self.environment.is_solved(lowest_cost_action[2]):
            lowest_cost_action = hq.heappop(self._queue)
            if self.expand_node(*lowest_cost_action):
                self.loop_counter.inc()

        return lowest_cost_action[1]


    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        self._queue = [] # array of (running_cost, [action_history], new_state) tuple
        self._visited_states = { self.environment.get_init_state(): 0 }
        lowest_cost_action = (0, 0, self.environment.get_init_state())
        self.expand_node(0, [], self.environment.get_init_state())
        self.loop_counter.inc()

        while not self.environment.is_solved(lowest_cost_action[2]):
            lowest_cost_action = hq.heappop(self._queue)
            self.expand_node(*lowest_cost_action)
            self.loop_counter.inc()

        return lowest_cost_action[1]


    def expand_node(self, running_cost: float, action_history: list, prev_state: State) -> bool:
        """
        Expands the node from prev_state by iterating through all possible actions and adding the tuple form to _queue.
        """
        new = False
        for action in ROBOT_ACTIONS:
            success, cost, state = self.environment.perform_action(prev_state, action)
            if success:
                if state not in self._visited_states or self._visited_states[state] > cost + running_cost:
                    history = action_history.copy()
                    history.append(action)
                    self._queue.append((cost + running_cost, history, state))
                    self._visited_states[state] = cost + running_cost
                    new = True

        return new
