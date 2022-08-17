from os import environ
import sys
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


class Node:
    """
    A generic node holding reference to 
    """
    def __init(self):
        pass


class Solver:

    def __init__(self, environment, loop_counter):
        self.environment = environment
        self.loop_counter = loop_counter

    def solve_ucs(self):
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """
        state = self.environment.get_init_state()
        state_history = []
        actions = []

        while not self.environment.is_solved(state):
            possible_actions = []

            # Find cost of each action
            success_fwd, cost_fwd, state_fwd = self.environment.perform_action(state, FORWARD)
            success_bwd, cost_bwd, state_bwd = self.environment.perform_action(state, REVERSE)
            success_spl, cost_spl, state_spl = self.environment.perform_action(state, SPIN_LEFT)
            success_spr, cost_spr, state_spr = self.environment.perform_action(state, SPIN_RIGHT)
            
            if success_fwd:
                possible_actions.append(FORWARD)
            if success_bwd:
                possible_actions.append(REVERSE)
            if success_spl:
                possible_actions.append(SPIN_LEFT)
            if success_spr:
                possible_actions.append(SPIN_RIGHT)

            self.loop_counter.inc()

        return actions
        

    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of ROBOT_ACTIONS)
        """

        #
        #
        # TODO: Implement your A* search code here
        #
        # === Important ================================================================================================
        # To ensure your code works correctly with tester, you should include the following line of code in your main
        # search loop:
        #
        # self.loop_counter.inc()
        #
        # e.g.
        # while loop_condition():
        #   self.loop_counter.inc()
        #   ...
        #
        # ==============================================================================================================
        #
        #

        pass
