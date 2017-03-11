#!/usr/bin/env python
# coding=UTF-8

from random import choice
from copy import deepcopy
from enum import Enum

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")


class Outcome(Enum):
    HUMAN = "human"
    AI = "ai"
    TIE = "tie"

    def congratulations(self):
        return {Outcome.HUMAN: "Human wins.", Outcome.AI: "AI wins.", Outcome.TIE: "Tie."}[self]


BLANK = " "
CROSS = "X"
NOUGHT = "O"
BOARD_SQUARE = "[{}]"

BOARD_SIDE_LENGTH = 3
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


class GameState:
    def __init__(self, previous_state=None, move=None):
        if previous_state is None:
            self.state = [BLANK] * BOARD_SIZE
            self.player = CROSS
        else:
            self.state = deepcopy(previous_state.state)
            self.state[move] = previous_state.player
            self.player = {CROSS: NOUGHT, NOUGHT: CROSS}[previous_state.player]

    def print_board(self):
        print(((BOARD_SQUARE * BOARD_SIDE_LENGTH + "\n") * BOARD_SIDE_LENGTH)
              .format(*[self.state[i] for i in range(BOARD_SIZE)]))

    def check_winner(self):
        for [a, b, c] in LINES:
            if self.state[a] is self.state[b] is self.state[c]:
                return self.state[a]

    def find_available(self):
        if self.check_winner() in [NOUGHT, CROSS]:
            return []
        else:
            return [i for i, x in enumerate(self.state) if x is BLANK]

    def next_states(self):
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


def min_play(state):
    if state.is_gameover():
        return evaluate(state)
    moves = state.get_available_moves()
    best_score = float('inf')
    for move in moves:
        clone = state.next_state(move)
        score = max_play(clone)
        if score < best_score:
            best_move = move
            best_score = score
    return best_score


def max_play(state):
    if state.is_gameover():
        return evaluate(state)
    moves = state.get_available_moves()
    best_score = float('-inf')
    for move in moves:
        clone = state.next_state(move)
        score = min_play(clone)
        if score > best_score:
            best_move = move
            best_score = score
    return best_score


def minimax(state, player):
    moves = state.find_available()
    best_move = moves[0]
    best_score = float('-inf')
    for move in moves:
        state = state.next_state(move, player)
        score = min_play(state)
        if score > best_score:
            best_move = move
            best_score = score
    return best_move


def take_turn_ai(state):
    print("AI's go:")
    return choice(state.next_states())


def play_round(state, start_human):
    (player_human, player_ai) = (CROSS, NOUGHT) if start_human else (NOUGHT, CROSS)

    while True:
        state = take_turn_human(state) if state.player is player_human else take_turn_ai(state)
        state.print_board()

        if not state.find_available():
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

        for outcome in Outcome:
            if winner is outcome:
                tallies[outcome] += 1

        if not prompt_boolean("\nPlay again? (Y/n): "):
            break

    print("\nHuman: {}\nAI:    {}\nTie:   {}"
          .format(*[tallies[outcome] for outcome in Outcome]))

if __name__ == "__main__":
    play_game()
