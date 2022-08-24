from os import environ
import sys
import math
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
        # list of (running_cost: float, [action_history]: list, new_state: State): tuple
        self.COST = 0
        self.HISTORY = 1
        self.STATE = 2
        self._ucs_queue = []
        self._a_queue = []
        self._visited_states = None # dictionary of { state: cost }


    def solve_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        self._visited_states = { self.environment.get_init_state(): 0 }
        lowest_queue = (0, 0, self.environment.get_init_state())
        self.expand_ucs_node(0, [], self.environment.get_init_state())

        while not self.environment.is_solved(lowest_queue[self.STATE]):
            lowest_queue = hq.heappop(self._ucs_queue)
            if self.expand_ucs_node(*lowest_queue):
                self.loop_counter.inc()

        return lowest_queue[self.HISTORY]


    def expand_ucs_node(self, running_cost: float, action_history: list, prev_state: State) -> bool:
        """
        Expands the node from prev_state by iterating through all possible actions and appending to the UCS queue.
        """
        new = False
        for action in ROBOT_ACTIONS:
            success, cost, state = self.environment.perform_action(prev_state, action)
            if success and (state not in self._visited_states or self._visited_states[state] > cost + running_cost):
                history = action_history.copy()
                history.append(action)
                self._ucs_queue.append((cost + running_cost, history, state))
                self._visited_states[state] = cost + running_cost
                new = True

        return new


    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        self._visited_states = { self.environment.get_init_state(): 0 }
        lowest_queue = (0, 0, self.environment.get_init_state())
        self.expand_a_node(0, [], self.environment.get_init_state())

        while not self.environment.is_solved(lowest_queue[self.STATE]):
            lowest_queue = hq.heappop(self._a_queue)
            if self.expand_a_node(*lowest_queue):
                self.loop_counter.inc()

        return lowest_queue[self.HISTORY]


    def expand_a_node(self, running_cost: float, action_history: list, prev_state: State) -> bool:
        """
        Expands the node from prev_state by iterating through all possible actions and appending to the A* queue.
        """
        new = False
        for action in ROBOT_ACTIONS:
            success, cost, state = self.environment.perform_action(prev_state, action)
            if success:
                total_cost = cost + running_cost + state.manhattan() #+ len(action_history) * 0.05
                # total_cost = cost + running_cost + state.manhattan_half() + len(action_history) * 0.05
                # total_cost = cost + running_cost + state.euclidean()
                if state not in self._visited_states or self._visited_states[state] > total_cost:
                    history = action_history.copy()
                    history.append(action)
                    self._a_queue.append((total_cost, history, state))
                    self._visited_states[state] = cost + running_cost
                    new = True

        return new
