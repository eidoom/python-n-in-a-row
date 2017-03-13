#!/usr/bin/env python
# coding=UTF-8

from argparse import ArgumentParser
from copy import deepcopy
from enum import Enum
from random import choice
from sys import exit
from time import clock

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")

INF = float('inf')

WIN_SCORE = INF
TIE_SCORE = 0
LOSE_SCORE = - WIN_SCORE

BLANK = " "
CROSS = "X"
NOUGHT = "O"

MINIMAX = "minimax"
RANDOM = "random"

parser = ArgumentParser()

parser.add_argument("-a", "--ai", type=str, default="{}".format(MINIMAX),
                    help="Set the computer AI: {} or {}".format(RANDOM, MINIMAX))
parser.add_argument("-y", "--board-height", type=int, default=3,
                    help="Set the board height (vertical side length.)")
parser.add_argument("-x", "--board-width", type=int, default=3,
                    help="Set the board width (horizontal side length).")
parser.add_argument("-s", "--square-board-side-length", type=int, default=None,
                    help="Set up a square board of desired side length (overrules other size settings).")
parser.add_argument("-n", "--row-length", type=int, default=3,
                    help="Set the game victory row length.")
parser.add_argument("-d", "--max-depth", type=int, default=10,
                    help="Set the AI maximum search depth (higher means more difficult opponent).")
parser.add_argument("-g", "--gravity", action="store_true", help="Turn on gravity.")
parser.add_argument("-q", "--quiet", action="store_true", help="Turn off excess verbosity.")

args = parser.parse_args()

BOARD_WIDTH = args.board_width
BOARD_HEIGHT = args.board_height
ROW_LENGTH = args.row_length

SQUARE_SIZE = args.square_board_side_length

if not (SQUARE_SIZE is None):
    BOARD_WIDTH = SQUARE_SIZE
    BOARD_HEIGHT = SQUARE_SIZE

if ROW_LENGTH > max(BOARD_WIDTH, BOARD_HEIGHT):
    exit("Impossible to win: victory row length too long for board size!")

BOARD_SIZE = BOARD_WIDTH * BOARD_HEIGHT

MAX_DEPTH = args.max_depth
GRAVITY = args.gravity
AI = args.ai
VERBOSE = not args.quiet

FIRST_TURN_RANDOM = True

BOARD_SQUARE = "[ {} ]" if GRAVITY else "[{}]"

HALF_DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1)]
DIRECTIONS = HALF_DIRECTIONS + [(-x, -y) for (x, y) in HALF_DIRECTIONS]


class Outcome(Enum):
    HUMAN = "human"
    AI = "ai"
    TIE = "tie"

    def congratulations(self):
        return {Outcome.HUMAN: "Human wins.", Outcome.AI: "AI wins.", Outcome.TIE: "Tie."}[self]


class GameState:
    def __init__(self, previous_state=None, move=None):
        if previous_state is None:
            self.state = [BLANK] * BOARD_SIZE
            self.player = CROSS
        else:
            self.state = deepcopy(previous_state.state)
            self.state[move] = previous_state.player
            self.player = self.get_other_player(previous_state.player)
        self.state_two = [[self.state[BOARD_WIDTH * i + j] for j in range(BOARD_WIDTH)]
                          for i in range(BOARD_HEIGHT)]

    @staticmethod
    def get_other_player(player):
        return {CROSS: NOUGHT, NOUGHT: CROSS}[player]

    def print_board(self):
        columns = (("  {}  " * BOARD_WIDTH).format(*[(i + 1) for i in range(BOARD_WIDTH)])) + "\n" if GRAVITY else ""
        print((columns + (BOARD_SQUARE * BOARD_WIDTH + "\n") * BOARD_HEIGHT)
              .format(*[self.state[i] for i in range(BOARD_SIZE)]))

    def count_line_length(self, position, direction, occupier, tally):
        i, j = [sum(x) for x in zip(position, direction)]
        if (0 <= i < BOARD_HEIGHT) and (0 <= j < BOARD_WIDTH):
            if self.state_two[i][j] is occupier:
                return self.count_line_length((i, j), direction, occupier, tally + 1)
        return tally

    def check_winner(self):
        for i, row in enumerate(self.state_two):
            for j, occupier in enumerate(row):
                if not (occupier is BLANK):
                    for direction in DIRECTIONS:
                        if self.count_line_length((i, j), direction, occupier, 1) == ROW_LENGTH:
                            return occupier

    def find_available(self):
        if self.check_winner() in [NOUGHT, CROSS]:
            return []
        elif GRAVITY:
            last_top_square = BOARD_SIZE - BOARD_WIDTH
            top_squares = self.state[:last_top_square]
            bottom_row = self.state[last_top_square:]
            available_bottom_squares = [last_top_square + i for i, x in enumerate(bottom_row)
                                        if x is BLANK]
            available_top_squares = [i for i, x in enumerate(top_squares) if (x is BLANK)
                                     and (self.state[i + BOARD_WIDTH] in (CROSS, NOUGHT))]
            return available_bottom_squares + available_top_squares
        else:
            return [i for i, x in enumerate(self.state) if x is BLANK]

    def check_game_over(self):
        return not self.find_available()

    def get_next_states(self):
        return [GameState(self, move) for move in self.find_available()]

    def evaluate_end(self):
        return {self.player: WIN_SCORE, self.get_other_player(self.player): LOSE_SCORE,
                None: TIE_SCORE}[self.check_winner()]

    def evaluate_cutoff(self):
        score = 0
        for i, row in enumerate(self.state_two):
            for j, occupier in enumerate(row):
                for direction in DIRECTIONS:
                    if occupier is self.player:
                        score += self.count_line_length((i, j), direction, occupier, 0)
                    elif occupier is self.get_other_player(self.player):
                        score -= self.count_line_length((i, j), direction, occupier, 0)
        return score


# ------------------------ negamax, alpha-beta, fail-soft

def negamax_play(alpha, beta, depth_left, state):
    if state.check_game_over():
        return state.evaluate_end(), state
    if depth_left == 0:
        return state.evaluate_cutoff(), state
    states = state.get_next_states()
    depth_left -= 1
    best_state = states[0]
    best_score = -INF
    for state in states:
        score = -negamax_play(-beta, -alpha, depth_left, state)[0]
        if score >= beta:
            return score, state
        elif score > best_score:
            best_score = score
            if score > alpha:
                alpha = score
                best_state = state
    return best_score, best_state


def minimax(state):
    alpha = -INF
    beta = INF
    depth_left = MAX_DEPTH
    state = negamax_play(alpha, beta, depth_left, state)[1]
    return state


# ----------------- negamax, list comprehension
#
# def negamax_play(state):
#     if state.check_game_over():
#         return -evaluate(state)
#     return min([-negamax_play(board_state) for board_state in state.get_next_states()])
#
#
# def minimax(state):
#     return max([(board_state, negamax_play(board_state))
#                 for board_state in state.get_next_states()],
#                key=lambda x: x[1])[0]

# ----------------- negamax, map
#
# def negamax_play(state):
#     if state.check_game_over():
#         return -evaluate(state)
#     return min(map(lambda board_state: -negamax_play(board_state), state.get_next_states()))
#
#
# def minimax(state):
#     return max(map(lambda board_state: (board_state, negamax_play(board_state)),
#                    state.get_next_states()), key=lambda x: x[1])[0]

# --------------------- minimax, concise, list comp.

# def min_play(state):
#     if state.check_game_over():
#         return -evaluate(state)
#     return min([max_play(board_state) for board_state in state.get_next_states()])
#
#
# def max_play(state):
#     if state.check_game_over():
#         return evaluate(state)
#     return max([min_play(board_state) for board_state in state.get_next_states()])
#
#
# def minimax(state):
#     return max([(board_state, min_play(board_state))
#                 for board_state in state.get_next_states()],
#                key=lambda x: x[1])[0]

# ------------------------ negamax, alpha-beta, fail-hard
#
# def negamax_play(alpha, beta, state):
#     if state.check_game_over():
#         return evaluate(state), state
#     states = state.get_next_states()
#     best_state = states[0]
#     for state in states:
#         score = -negamax_play(-beta, -alpha, state)[0]
#         if score >= beta:
#             return beta, state
#         elif score > alpha:
#             alpha = score
#             best_state = state
#     return alpha, best_state
#
#
# def minimax(state):
#     alpha = -INF
#     beta = INF
#     state = negamax_play(alpha, beta, state)[1]
#     return state



# ------------------------ minimax, standard

# def min_play(state):
#     if state.check_game_over():
#         return -evaluate(state)
#     states = state.get_next_states()
#     best_score = INF
#     for state in states:
#         score = max_play(state)
#         if score < best_score:
#             # best_states = state
#             best_score = score
#     return best_score
#
#
# def max_play(state):
#     if state.check_game_over():
#         return evaluate(state)
#     states = state.get_next_states()
#     best_score = INF
#     for state in states:
#         score = min_play(state)
#         if score > best_score:
#             # best_state = state
#             best_score = score
#     return best_score
#
#
# def minimax(state):
#     states = state.get_next_states()
#     best_state = states[0]
#     best_score = -INF
#     for state in states:
#         score = min_play(state)
#         if score > best_score:
#             best_state = state
#             best_score = score
#     return best_state

# ------------------------- minimax, alpha-beta
#
# def min_play(alpha, beta, state):
#     if state.check_game_over():
#         return -evaluate(state), state
#     else:
#         states = state.get_next_states()
#         best_state = states[0]
#         for state in states:
#             score = max_play(alpha, beta, state)[0]
#             if score <= alpha:
#                 return alpha, state
#             elif score < beta:
#                 best_state = state
#                 beta = score
#         return beta, best_state
#
#
# def max_play(alpha, beta, state):
#     if state.check_game_over():
#         return evaluate(state), state
#     else:
#         states = state.get_next_states()
#         best_state = states[0]
#         for state in states:
#             score = min_play(alpha, beta, state)[0]
#             if score >= beta:
#                 return beta, state
#             elif score > alpha:
#                 best_state = state
#                 alpha = score
#         return alpha, best_state
#
#
# def minimax(state):
#     alpha = -INF
#     beta = INF
#     state = min_play(alpha, beta, state)[1]
#     return state
#
#
# -------------------------


def take_turn_ai(state, decision):
    print("AI's go:")
    start_time = clock()
    if decision is MINIMAX:
        result = minimax(state)
    elif decision is RANDOM:
        result = choice(state.get_next_states())
    else:
        exit("Sorry, AI {} is unsupported.".format(AI))
    if VERBOSE:
        print("Time: {}".format(clock() - start_time))
    return result


def take_turn_human(state):
    while True:
        try:
            move = int(input("Your go: ")) - 1

            if GRAVITY:
                available = state.find_available()
                coords = [(number // BOARD_WIDTH, number % BOARD_WIDTH) for number in available]
                for i, j in coords:
                    if j == move:
                        position = i * BOARD_WIDTH + j
                        return GameState(state, position)

            else:
                if move in state.find_available():
                    return GameState(state, move)

        except ValueError:
            print("Really?")


def prompt_boolean(prompt):
    while True:
        input_char = input(prompt)

        if input_char in NO:
            return False
        elif input_char in YES:
            return True
        else:
            print("What?")


def play_round(state, start_human):
    (player_human, player_ai) = (CROSS, NOUGHT) if start_human else (NOUGHT, CROSS)

    if FIRST_TURN_RANDOM and (not start_human):
        state = take_turn_ai(state, RANDOM)
        state.print_board()

    while True:

        state = take_turn_human(state) if state.player is player_human else take_turn_ai(state, AI)

        state.print_board()

        if state.check_game_over():
            break

    winner = state.check_winner()

    return {player_human: Outcome.HUMAN, player_ai: Outcome.AI, None: Outcome.TIE}[winner]


def play_game():
    tallies = {outcome: 0 for outcome in Outcome}

    while True:
        state = GameState()
        state.print_board()

        start_human = prompt_boolean("Wanna start? ")

        winner = play_round(state, start_human)

        print(winner.congratulations())
        tallies[winner] += 1

        if not prompt_boolean("\nPlay again? "):
            break

    print("\nHuman: {}\nAI:    {}\nTie:   {}".format(*[tallies[outcome] for outcome in Outcome]))


def main():
    play_game()


if __name__ == "__main__":
    main()
