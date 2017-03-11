# coding=UTF-8

from random import choice

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")

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

LINES = HORIZONTAL_LINES + VERTICAL_LINES + DIAGONAL_LINE + ANTI_DIAGONAL_LINE

ALL_LINES = LINES + [line[::-1] for line in LINES]

state = [BLANK] * BOARD_SIZE
tallies = [0] * 3


def prompt_boolean(prompt):
    while True:
        input_char = input(prompt)

        if input_char in NO:
            return False
        elif input_char in YES:
            return True
        else:
            print("What?")


def print_board():
    print(((BOARD_SQUARE * BOARD_SIDE_LENGTH + "\n") * BOARD_SIDE_LENGTH)
          .format(*[state[i] for i in range(BOARD_SIZE)]))


def find_available():
    return [i for i, x in enumerate(state) if x is BLANK]


def check_winner():
    for [a, b, c] in LINES:
        if state[a] is state[b] is state[c]:
            return state[a]


def take_turn_human(player):
    while True:
        try:
            move = int(input("Your go: ")) - 1

            if move in find_available():
                break
        except ValueError:
            print("Really?")

    state[move] = player


def take_turn_ai(player):
    print("AI's go:")
    move = choice(find_available())

    state[move] = player


def play_round():
    print_board()

    if prompt_boolean("Wanna start? "):
        player_human = CROSS
        player_ai = NOUGHT
        turn_human = True
    else:
        player_human = NOUGHT
        player_ai = CROSS
        turn_human = False

    while True:
        if turn_human:
            take_turn_human(player_human)

        else:
            take_turn_ai(player_ai)

        print_board()

        winner = check_winner()

        if (not find_available()) or (winner in [NOUGHT, CROSS]):
            break

        turn_human = not turn_human

    if winner is player_human:
        tallies[0] += 1
        print("Human wins.")
    elif winner is player_ai:
        tallies[1] += 1
        print("AI wins.")
    elif winner is None:
        tallies[2] += 1
        print("Tie.")


def play_game():
    while True:
        play_round()

        if not prompt_boolean("\nPlay again? (Y/n): "):
            print("\nHuman: {}\nAI:    {}\nTie:   {}".format(*tallies))
            break


if __name__ == "__main__":
    play_game()
