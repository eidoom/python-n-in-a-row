#!/usr/bin/env python
# coding=UTF-8

from argparse import ArgumentParser
from copy import deepcopy
from enum import Enum
from time import clock

# from random import choice

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")

WIN_SCORE = 1
TIE_SCORE = 0
LOSE_SCORE = - WIN_SCORE

INF = float('inf')

BLANK = " "
CROSS = "X"
NOUGHT = "O"
BOARD_SQUARE = "[{}]"

parser = ArgumentParser()
parser.add_argument(
    "-l", "--side-length", type=int, default=3, help="Set the board side length.")
args = parser.parse_args()
BOARD_SIDE_LENGTH = args.side_length

BOARD_SIZE = BOARD_SIDE_LENGTH ** 2

POSITIONS = [[BOARD_SIDE_LENGTH * i + j for j in range(BOARD_SIDE_LENGTH)]
             for i in range(BOARD_SIDE_LENGTH)]

HORIZONTAL_LINES = [POSITIONS[i] for i in range(BOARD_SIDE_LENGTH)]
VERTICAL_LINES = [[POSITIONS[i][j] for i in range(BOARD_SIDE_LENGTH)]
                  for j in range(BOARD_SIDE_LENGTH)]
DIAGONAL_LINE = [[POSITIONS[i][i] for i in range(BOARD_SIDE_LENGTH)]]
ANTI_DIAGONAL_LINE = [[POSITIONS[i][BOARD_SIDE_LENGTH - 1 - i]
                       for i in range(BOARD_SIDE_LENGTH)]]

LINES = (HORIZONTAL_LINES + VERTICAL_LINES + DIAGONAL_LINE
         + ANTI_DIAGONAL_LINE)

ALL_LINES = LINES + [line[::-1] for line in LINES]


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

    @staticmethod
    def get_other_player(player):
        return {CROSS: NOUGHT, NOUGHT: CROSS}[player]

    def print_board(self):
        print(((BOARD_SQUARE * BOARD_SIDE_LENGTH + "\n") * BOARD_SIDE_LENGTH)
              .format(*[self.state[i] for i in range(BOARD_SIZE)]))

    def check_winner(self):
        for line in LINES:
            a = line[0]
            if (len(set([self.state[i] for i in line])) == 1) and (self.state[a] is not BLANK):
                return self.state[a]

    def find_available(self):
        if self.check_winner() in [NOUGHT, CROSS]:
            return []
        elif BOARD_SIDE_LENGTH > 3:
            last_top_square = BOARD_SIZE - BOARD_SIDE_LENGTH
            top_squares = self.state[:last_top_square]
            bottom_row = self.state[last_top_square:]
            available_bottom_squares = [last_top_square + i for i, x in enumerate(bottom_row)
                                        if x is BLANK]
            available_top_squares = [i for i, x in enumerate(top_squares)
                                     if (x is BLANK)
                                     and (self.state[i + BOARD_SIDE_LENGTH] in (CROSS, NOUGHT))]
            return available_bottom_squares + available_top_squares
        else:
            return [i for i, x in enumerate(self.state) if x is BLANK]

    def check_game_over(self):
        return not self.find_available()

    def get_next_states(self):
        return [GameState(self, move) for move in self.find_available()]


def prompt_boolean(prompt):
    while True:
        input_char = input(prompt)

        if input_char in NO:
            return False
        elif input_char in YES:
            return True
        else:
            print("What?")


def take_turn_human(state):
    while True:
        try:
            move = int(input("Your go: ")) - 1

            if move in state.find_available():
                return GameState(state, move)
        except ValueError:
            print("Really?")


def evaluate(state):
    return {state.player: WIN_SCORE, state.get_other_player(state.player): LOSE_SCORE,
            None: TIE_SCORE}[state.check_winner()]


# -----------------

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

# -----------------
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

# ---------------------

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

# ------------------------

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

# -------------------------

def min_play(alpha, beta, state):
    if state.check_game_over():
        return -evaluate(state), state
    else:
        states = state.get_next_states()
        best_state = states[0]
        for state in states:
            score = max_play(alpha, beta, state)[0]
            if score <= alpha:
                return alpha, state
            elif score < beta:
                best_state = state
                beta = score
        return beta, best_state


def max_play(alpha, beta, state):
    if state.check_game_over():
        return evaluate(state), state
    else:
        states = state.get_next_states()
        best_state = states[0]
        for state in states:
            score = min_play(alpha, beta, state)[0]
            if score >= beta:
                return beta, state
            elif score > alpha:
                best_state = state
                alpha = score
        return alpha, best_state


def minimax(state):
    alpha = -INF
    beta = INF
    state = min_play(alpha, beta, state)[1]
    return state


# -------------------------


def take_turn_ai(state):
    print("AI's go:")
    start_time = clock()
    result = minimax(state)
    print("Time: {}".format(clock() - start_time))
    return result


# def take_turn_ai_random(state):
#     print("AI's go:")
#     return choice(state.get_next_states())


def play_round(state, start_human):
    (player_human, player_ai) = (CROSS, NOUGHT) if start_human else (NOUGHT, CROSS)

    while True:
        state = take_turn_human(state) if state.player is player_human else take_turn_ai(state)
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

    print("\nHuman: {}\nAI:    {}\nTie:   {}"
          .format(*[tallies[outcome] for outcome in Outcome]))


def main():
    play_game()


if __name__ == "__main__":
    main()
