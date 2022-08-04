import sys
import time
import math
import json

from constants import *
from environment import Environment

from solution import Solver

"""
Tester script.

Use this script to evaluate your solution. You may modify this file if desired. When submitting to GradeScope, an
unmodified version of this file will be used to evaluate your code.

COMP3702 2022 Assignment 1 Support Code

Last updated by njc 04/08/22
"""

TC_PREFIX = 'testcases/ex'
TC_SUFFIX = '.txt'
FORCE_VALID = True
DISABLE_TIME_LIMITS = True

ACTION_READABLE = {FORWARD: 'Forward', REVERSE: 'Reverse', SPIN_LEFT: 'Spin Left',
                   SPIN_RIGHT: 'Spin Right'}

# 6 points for each (method, testcase pair)
# 2 points for cost (scaling up to 2x tgt)
# 2 points for timing (scaling up to 2x tgt)
# 2 points for nodes expanded (scaling up to 2x tgt)
POINTS_PER_TESTCASE = 6.0
COMPLETION_POINTS = 1.5
COST_POINTS = 1.5
COST_SCALING = 1.0
TIMING_POINTS = 1.5
TIMING_SCALING = 1.0
EXPAND_POINTS = 1.5
EXPAND_SCALING = 1.0
MINIMUM_MARK_INCREMENT = 0.1


class LoopCounter:
    # Used to record the number of loop iterations (e.g. number of nodes expanded) and monitor for unrealistic behaviour
    # (if the average time between increments is too small, then fail verification).

    def __init__(self):
        self._last_inc_time = time.time()
        self._last_inc_count = 0
        self._count = 0
        self.violations = 0

        self._ts = []

    def inc(self):
        self._count += 1

        if self._count - self._last_inc_count > 50:
            t = time.time()
            self._ts.append(t - self._last_inc_time)
            self._last_inc_time = t
            self._last_inc_count = self._count

    def count(self):
        return self._count

    def verify1(self, tgt, s_type):
        # Return False if count is too low relative to the target, suggesting counter was used incorrectly
        if s_type == 'ucs':
            return self._count > (tgt * 0.8)
        else:
            return self._count > (tgt * 0.2)

    def verify2(self):
        # return False if timing suggests loop counter was used incorrectly
        ts_avg = sum(self._ts) / len(self._ts)
        if ts_avg < 0.0005:
            return False
        else:
            return True


def print_usage():
    print("Usage: python tester.pyc [search_type] [testcases] [-v (optional)]")
    print("    search_type = 'ucs', 'a_star' or 'both'")
    print("    testcases = a comma separated list of numbers (e.g. '1,3,4')")
    print("    if -v is specified, the solver's trajectory will be visualised")


def compute_score(points, scaling, actual, target):
    return points * (1.0 - min(max(actual - target, 0) / (scaling * target), 1.0))


def update_logfile(filename, search_type, tc_idx, total_score, max_score, tests):
    total_score = math.ceil(total_score * (1 / MINIMUM_MARK_INCREMENT)) / (1 / MINIMUM_MARK_INCREMENT)
    msg0 = '\n\n=== Summary ============================================================'
    msg1 = f'Search type: {search_type},   Testcases: {tc_idx}'
    msg2 = f'Total Score: {round(total_score, 2)} (out of max possible score {max_score})'
    log_data = {"output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n', "tests": tests}
    with open(filename, 'w') as outfile:
        json.dump(log_data, outfile)
    pass


def main(arglist):

    # parse command line arguments
    if len(arglist) != 2 and len(arglist) != 3 and len(arglist) != 4:
        print("Run this script to test and evaluate the performance of your code.\n")
        print_usage()
        return

    search_type = arglist[0]
    if search_type not in ['ucs', 'a_star', 'both']:
        print("Invalid search_type given.")
        print_usage()
        return
    search_types = [search_type] if search_type != 'both' else ['ucs', 'a_star']

    try:
        tc_idx = [int(i) for i in arglist[1].split(',')]
    except ValueError:
        print("Invalid testcases list given.")
        print_usage()
        return

    visualise = False
    write_logfile = False
    results_filename = None
    i = 2
    while i < len(arglist):
        if arglist[i] == '-v':
            visualise = True
            i += 1
        elif arglist[i] == '-l':
            assert len(arglist) > i + 1, '/!\\ write_logfile is enabled but no filename is given'
            write_logfile = True
            results_filename = arglist[i + 1]
            i += 2
        else:
            print("Unrecognised command line argument given.")
            print_usage()
            return

    total_score = 0.0
    max_score = POINTS_PER_TESTCASE * len(tc_idx) * (2.0 if search_type == 'both' else 1.0)
    tests = []

    # loop over all selected testcases
    for i in tc_idx:
        tc_filename = TC_PREFIX + str(i) + TC_SUFFIX
        env = Environment(tc_filename, FORCE_VALID)

        for s in search_types:
            msg0 = f'=== Testcase {i}, {"UCS" if s == "ucs" else "A*"} ' \
                   f'============================================================'
            print(msg0)

            lc = LoopCounter()
            t0 = time.time()
            solver = Solver(env, lc)
            t_init = time.time() - t0
            if t_init > 0.001 and not DISABLE_TIME_LIMITS:
                msg1 = 'Your __init__ method appears to be taking a long time to complete. Make sure any expensive ' \
                       'computations (e.g. pre-computing data for a heuristic) are in solve_ucs or solve a_star ' \
                       'instead of __init__.\n'
                print(msg1)
                msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                print(msg2)
                tests.append({"score": 0,
                              "max_score": POINTS_PER_TESTCASE,
                              "output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n'})
                if write_logfile:
                    update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                continue
            if s == 'ucs':
                # call student's solve_ucs
                t0 = time.time()
                try:
                    path = solver.solve_ucs()
                except BaseException as e:
                    msg1 = f'Program crashed in solve_ucs() on testcase {i}'
                    print(msg1)
                    print(e)
                    msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                    print(msg2)
                    tests.append({"score": 0,
                                  "max_score": POINTS_PER_TESTCASE,
                                  "output": msg0 + '\n' + msg1 + '\n' + str(e) + '\n' + msg2 + '\n'})
                    if write_logfile:
                        update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                    continue
                t_solve = time.time() - t0
            else:
                # call student's solve_a_star
                t0 = time.time()
                try:
                    path = solver.solve_a_star()
                except BaseException as e:
                    msg1 = f'Program crashed in solve_a_star() on testcase {i}'
                    print(msg1 + '\n')
                    print(e)
                    msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                    print(msg2)
                    tests.append({"score": 0,
                                  "max_score": POINTS_PER_TESTCASE,
                                  "output": msg0 + '\n' + msg1 + '\n' + str(e) + '\n' + msg2 + '\n'})
                    if write_logfile:
                        update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                    continue
                t_solve = time.time() - t0
            # check that loop counter was used legitimately
            if not lc.verify1(env.cost_tgt, s):
                msg1 = f'Your search expanded an unrealistically low number of nodes {s}. Please check that this ' \
                       f'search type is implemented, and that "self.loop_counter.inc()" is called in the correct place.'
                print(msg1)
                msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                print(msg2)
                tests.append({"score": 0,
                              "max_score": POINTS_PER_TESTCASE,
                              "output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n'})
                if write_logfile:
                    update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                continue
            if not lc.verify2():
                msg1 = f'Your search loop appears to be running unrealistically quickly for {s}. Please check that ' \
                       f'this search type is implemented, and that "self.loop_counter.inc()" is called in the ' \
                       f'correct place.'
                print(msg1)
                msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                print(msg2)
                tests.append({"score": 0,
                              "max_score": POINTS_PER_TESTCASE,
                              "output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n'})
                if write_logfile:
                    update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                continue

            # verify path
            state = env.get_init_state()
            total_cost = 0.0
            if visualise:
                env.render(state)
            for j, action in enumerate(path):
                if visualise:
                    print(f'\nSelected: {ACTION_READABLE[action]}')
                success, cost, new_state = env.perform_action(state, action)
                if not success:
                    msg1 = f'/!\\ Action {j} resulted in collision.'
                    print(msg1)
                    msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                    print(msg2)
                    tests.append({"score": 0,
                                  "max_score": POINTS_PER_TESTCASE,
                                  "output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n'})
                    if write_logfile:
                        update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
                    continue
                else:
                    total_cost += cost
                    state = new_state
                if visualise:
                    env.render(state)

            if env.is_solved(state):
                # record statistics
                cost_score = compute_score(COST_POINTS, COST_SCALING, total_cost, env.cost_tgt)

                time_tgt = env.time_tgt[0 if s == 'ucs' else 1]
                timing_score = compute_score(TIMING_POINTS, TIMING_SCALING, t_solve, time_tgt)

                exp_tgt = env.exp_tgt[0 if s == 'ucs' else 1]
                exp_score = compute_score(EXPAND_POINTS, EXPAND_SCALING, lc.count(), exp_tgt)

                tc_total_score = COMPLETION_POINTS + cost_score + timing_score + exp_score
                total_score += tc_total_score

                # round before printing (but after computing score)
                total_cost = round(total_cost, 1)
                t_solve = round(t_solve, 3)
                tc_total_score = round(tc_total_score, 2)
                msg1 = f'Agent successfully reached the goal --> Score: {COMPLETION_POINTS} / {COMPLETION_POINTS}'
                msg2 = f'Path Cost: {total_cost},    Target: {env.cost_tgt}  ' \
                       f'--> Score: {round(cost_score, 1)} / {COST_POINTS}'
                print(msg2)
                msg3 = f'Time Elapsed: {t_solve},    Target: {time_tgt}  ' \
                       f'--> Score: {round(timing_score, 1)} / {TIMING_POINTS}'
                print(msg3)
                msg4 = f'Nodes Expanded: {lc.count()},    Target: {exp_tgt}  ' \
                       f'--> Score: {round(exp_score, 1)} / {TIMING_POINTS}'
                print(msg4)
                msg5 = f'\nTestcase total score: {tc_total_score} / {POINTS_PER_TESTCASE}'
                print(msg5)
                tests.append({"score": tc_total_score,
                              "max_score": POINTS_PER_TESTCASE,
                              "output": (msg0 + '\n' + msg1 + '\n' + msg2 + '\n' + msg3 + '\n' + msg4 + '\n' +
                                         msg5 + '\n')})
                if write_logfile:
                    update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
            else:
                msg1 = f'/!\\ Path did not result in agent reaching the goal.'
                print(msg1)
                msg2 = f'\nTestcase total score: 0.0 / {POINTS_PER_TESTCASE}'
                print(msg2)
                tests.append({"score": 0,
                              "max_score": POINTS_PER_TESTCASE,
                              "output": msg0 + '\n' + msg1 + '\n' + msg2 + '\n'})
                if write_logfile:
                    update_logfile(results_filename, search_type, tc_idx, total_score, max_score, tests)
            print('\n')

    total_score = math.ceil(total_score * (1 / MINIMUM_MARK_INCREMENT)) / (1 / MINIMUM_MARK_INCREMENT)

    msg0 = '\n\n=== Summary ============================================================'
    print(msg0)
    msg1 = f'Search type: {search_type},   Testcases: {tc_idx}'
    print(msg1)
    msg2 = f'Total Score: {round(total_score, 2)} (out of max possible score {max_score})'
    print(msg2)


if __name__ == '__main__':
    main(sys.argv[1:])



