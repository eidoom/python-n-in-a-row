#!/usr/bin/env python3
# coding=UTF-8

from argparse import ArgumentParser
from copy import deepcopy
from enum import Enum
from random import choice
from sys import exit
from time import perf_counter

W = 50
HR = "-" * W

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")

INF = float("inf")

BLANK = " "
CROSS = "X"
NOUGHT = "O"

# to stop crazy analysis for first play when AI goes first
FIRST_TURN_RANDOM = True

MINIMAX = "minimax"
RANDOM = "random"

HALF_DIRECTIONS = [(-1, 0), (-1, 1), (0, 1), (1, 1)]


class Outcome(Enum):
    HUMAN = "human"
    AI = "ai"
    TIE = "tie"

    def congratulations(self):
        return {
            Outcome.HUMAN: "Human wins.",
            Outcome.AI: "AI wins.",
            Outcome.TIE: "Tie.",
        }[self]


def print_board_frame(entries):
    print(((BOARD_SQUARE * BOARD_WIDTH + "\n") * BOARD_HEIGHT).format(*entries))


class GameState:
    def __init__(self, previous_state=None, move=None):
        if previous_state is None:
            self.state = [BLANK] * BOARD_SIZE
            self.player = CROSS  # crosses start
        else:
            self.state = deepcopy(previous_state.state)
            self.state[move] = previous_state.player
            self.player = self.get_other_player(previous_state.player)

        self.state_two = [
            [self.state[BOARD_WIDTH * i + j] for j in range(BOARD_WIDTH)]
            for i in range(BOARD_HEIGHT)
        ]

    @staticmethod
    def get_other_player(player):
        return {CROSS: NOUGHT, NOUGHT: CROSS}[player]

    def print_board(self):
        column_numbers = (
            ("  {}  " * BOARD_WIDTH).format(*[(i + 1) for i in range(BOARD_WIDTH)])
            + "\n"
            if GRAVITY
            else ""
        )
        print(column_numbers)
        print_board_frame([self.state[i] for i in range(BOARD_SIZE)])

    def check_position(self, i, j, occupier):
        return (
            (0 <= i < BOARD_HEIGHT)
            and (0 <= j < BOARD_WIDTH)
            and self.state_two[i][j] == occupier
        )

    def count_line_length(self, i, j, di, dj, occupier, tally=1):
        if tally != ROW_LENGTH:
            ni, nj = (i + di, j + dj)
            if self.check_position(ni, nj, occupier):
                return self.count_line_length(ni, nj, di, dj, occupier, tally + 1)

        return tally

    def check_winner(self):
        for i, row in enumerate(self.state_two):
            for j, occupier in enumerate(row):
                if occupier != BLANK:
                    for direction in HALF_DIRECTIONS:
                        if (
                            self.count_line_length(i, j, *direction, occupier, 1)
                            == ROW_LENGTH
                        ):
                            return occupier

    def find_available(self):
        if self.check_winner() in [NOUGHT, CROSS]:
            return []

        if GRAVITY:
            last_top_square = BOARD_SIZE - BOARD_WIDTH
            top_squares = self.state[:last_top_square]
            bottom_row = self.state[last_top_square:]
            available_bottom_squares = [
                last_top_square + i for i, x in enumerate(bottom_row) if x == BLANK
            ]
            available_top_squares = [
                i
                for i, x in enumerate(top_squares)
                if (x == BLANK) and (self.state[i + BOARD_WIDTH] in (CROSS, NOUGHT))
            ]
            return available_bottom_squares + available_top_squares
        else:
            return [i for i, x in enumerate(self.state) if x == BLANK]

    def check_game_over(self):
        return not self.find_available()

    def get_next_states(self):
        return [GameState(self, move) for move in self.find_available()]

    def evaluate(self):
        winner = self.check_winner()

        if winner is not None:
            score = WIN_SCORE if winner == self.player else LOSE_SCORE

            if DEBUG:
                self.print_board()
                print(f"Score:  {score}")
                print(f"Winner: {winner}")

        else:
            if DEBUG:
                print()

            score = 0
            for i, row in enumerate(self.state_two):
                for j, occupier in enumerate(row):
                    for direction in HALF_DIRECTIONS:
                        if occupier != BLANK:
                            n = self.count_line_length(i, j, *direction, occupier)
                            # could also check next square of line is a blank
                            if n > 1:
                                if DEBUG:
                                    print(
                                        f"counting {occupier} on {(i,j)} going {direction}: {n}"
                                    )

                                score += n if occupier == self.player else -n

            if DEBUG:
                self.print_board()
                print(f"Score: {score}")

        return score


# ------------------------ negamax, alpha-beta, fail-soft


def negamax_play(alpha, beta, depth_left, state):
    # https://www.chessprogramming.org/Alpha-Beta#Outside_the_Bounds
    if state.check_game_over() or not depth_left:
        return state.evaluate(), state

    states = state.get_next_states()
    best_state = states[0]
    best_score = -INF
    for state in states:
        score = -negamax_play(-beta, -alpha, depth_left - 1, state)[0]
        if score >= beta:
            # fail-soft beta-cutoff
            return score, state
        elif score > best_score:
            best_score = score
            best_state = state
            if score > alpha:
                alpha = score
    return best_score, best_state


def minimax(state):
    alpha = -INF  # upper bound
    beta = INF  # lower bound
    depth_left = MAX_DEPTH
    score, state = negamax_play(alpha, beta, depth_left, state)
    if DEBUG:
        print(HR + f"\nbest score: {score}")
    return state


# ------------------------


def take_turn_ai(state, decision):
    print("AI's go:")

    start_time = perf_counter()

    if DEBUG:
        print(HR)
        print(f"Outcomes after {MAX_DEPTH} moves")

    if decision == MINIMAX:
        result = minimax(state)
    elif decision == RANDOM:
        result = choice(state.get_next_states())
    else:
        exit(f"Sorry, AI {AI} is unsupported.")

    if DEBUG:
        print(HR)

    if VERBOSE:
        print(f"Time: {perf_counter() - start_time:.3f}s")

    return result


def take_turn_human(state):
    while True:
        try:
            move = int(input("Your go: ")) - 1

            if GRAVITY:
                available = state.find_available()
                coords = [
                    (number // BOARD_WIDTH, number % BOARD_WIDTH)
                    for number in available
                ]
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
        state = (
            take_turn_human(state)
            if state.player == player_human
            else take_turn_ai(state, AI)
        )

        state.print_board()

        if state.check_game_over():
            break

    winner = state.check_winner()

    return {
        player_human: Outcome.HUMAN,
        player_ai: Outcome.AI,
        None: Outcome.TIE,
    }[winner]


def play_game():
    tallies = {outcome: 0 for outcome in Outcome}

    while True:
        state = GameState()
        state.print_board()

        start_human = PIECE == CROSS or (
            PIECE is None and prompt_boolean("Wanna start? ")
        )

        winner = play_round(state, start_human)

        print(winner.congratulations())
        tallies[winner] += 1

        if not prompt_boolean("\nPlay again? "):
            break

    print(
        "\nHuman: {}\nAI:    {}\nTie:   {}".format(
            *[tallies[outcome] for outcome in Outcome]
        )
    )


def get_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-a",
        "--ai",
        type=str,
        default=MINIMAX,
        help=f"Set the computer AI: {RANDOM} or {MINIMAX}",
    )
    parser.add_argument(
        "-y",
        "--board-height",
        type=int,
        default=3,
        help="Set the board height (vertical side length.)",
    )
    parser.add_argument(
        "-x",
        "--board-width",
        type=int,
        default=3,
        help="Set the board width (horizontal side length).",
    )
    parser.add_argument(
        "-s",
        "--square-board-side-length",
        type=int,
        default=None,
        help="Set up a square board of desired side length "
        "(overrules other size settings).",
    )
    parser.add_argument(
        "-n",
        "--row-length",
        type=int,
        default=3,
        help="Set the game victory row length.",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=5,
        help="Set the AI maximum search depth "
        "(higher means more difficult opponent).",
    )
    parser.add_argument(
        "-g",
        "--gravity",
        action="store_true",
        help="Turn on gravity.",
    )
    parser.add_argument(
        "-p",
        "--piece",
        type=str,
        choices=(CROSS, NOUGHT),
        help=f"Choose the piece to play. {CROSS}s start.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Turn off excess verbosity.",
    )
    parser.add_argument(
        "-v",
        "--debug",
        action="store_true",
        help="Turn on debugging output.",
    )

    return parser.parse_args()


def main():
    global AI
    global BOARD_HEIGHT
    global BOARD_SIZE
    global BOARD_SQUARE
    global BOARD_WIDTH
    global DEBUG
    global GRAVITY
    global LOSE_SCORE
    global MAX_DEPTH
    global ROW_LENGTH
    global TIE_SCORE
    global VERBOSE
    global WIN_SCORE
    global PIECE

    args = get_args()

    BOARD_WIDTH = args.board_width
    BOARD_HEIGHT = args.board_height
    ROW_LENGTH = args.row_length

    SQUARE_SIZE = args.square_board_side_length

    if SQUARE_SIZE is not None:
        BOARD_WIDTH = SQUARE_SIZE
        BOARD_HEIGHT = SQUARE_SIZE

    if ROW_LENGTH > max(BOARD_WIDTH, BOARD_HEIGHT):
        exit("Impossible to win: victory row length too long for board size!")

    BOARD_SIZE = BOARD_WIDTH * BOARD_HEIGHT

    MAX_DEPTH = args.max_depth
    GRAVITY = args.gravity
    AI = args.ai
    VERBOSE = not args.quiet
    DEBUG = args.debug

    PIECE = args.piece

    BOARD_SQUARE = "[ {} ]" if GRAVITY else "[{}]"

    WIN_SCORE = float("inf")
    TIE_SCORE = 0
    LOSE_SCORE = -WIN_SCORE

    print(
        f"Game initialised with AI {AI} of depth {MAX_DEPTH}, victory row length {ROW_LENGTH}"
        f" and {'vertical' if GRAVITY else 'horizontal'} board{'' if GRAVITY else ' with square names'}:"
    )

    if not GRAVITY:
        if BOARD_SIZE < 10:
            numbers = range(1, BOARD_SIZE + 1)
        else:
            numbers = [f" {i}" for i in range(1, 10)] + [
                str(i) for i in range(10, BOARD_SIZE + 1)
            ]
        print_board_frame(numbers)

    play_game()


if __name__ == "__main__":
    main()
