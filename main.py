# coding=UTF-8

from random import choice

YES = ("", "y", "Y", "Yes", "yes")
NO = ("n", "N", "No", "no")

HUMAN = "human"
AI = "ai"
TIE = "tie"

OUTCOMES = (HUMAN, AI, TIE)


def prompt_boolean(prompt):
    while True:
        input_char = input(prompt)

        if input_char in NO:
            return False
        elif input_char in YES:
            return True
        else:
            print("What?")


class NInARow:
    def __init__(self):
        self.blank = " "
        self.cross = "X"
        self.nought = "O"
        self.board_square = "[{}]"

        self.board_side_length = 3
        self.board_size = self.board_side_length ** 2

        self.positions = [[self.board_side_length * i + j for j in range(self.board_side_length)]
                          for i in range(self.board_side_length)]

        self.horizontal_lines = [self.positions[i] for i in range(self.board_side_length)]
        self.vertical_lines = [[self.positions[i][j] for i in range(self.board_side_length)]
                               for j in range(self.board_side_length)]
        self.diagonal_line = [[self.positions[i][i] for i in range(self.board_side_length)]]
        self.anti_diagonal_line = [[self.positions[i][self.board_side_length - 1 - i]
                                    for i in range(self.board_side_length)]]

        self.lines = (self.horizontal_lines + self.vertical_lines + self.diagonal_line
                      + self.anti_diagonal_line)

        self.all_lines = self.lines + [line[::-1] for line in self.lines]

        self.state = [self.blank] * self.board_size

    def print_board(self):
        print(((self.board_square * self.board_side_length + "\n") * self.board_side_length)
              .format(*[self.state[i] for i in range(self.board_size)]))

    def find_available(self):
        return [i for i, x in enumerate(self.state) if x is self.blank]

    def check_winner(self):
        for [a, b, c] in self.lines:
            if self.state[a] is self.state[b] is self.state[c]:
                return self.state[a]

    def check_game_over(self, winner):
        return (not self.find_available()) or (winner in [self.nought, self.cross])

    def take_turn_human(self, player):
        while True:
            try:
                move = int(input("Your go: ")) - 1

                if move in self.find_available():
                    break
            except ValueError:
                print("Really?")

        self.state[move] = player

    def take_turn_ai(self, player):
        print("AI's go:")
        move = choice(self.find_available())

        self.state[move] = player


def play_round():
    game = NInARow()
    game.print_board()

    if prompt_boolean("Wanna start? "):
        player_human = game.cross
        player_ai = game.nought
        turn_human = True
    else:
        player_human = game.nought
        player_ai = game.cross
        turn_human = False

    while True:
        if turn_human:
            game.take_turn_human(player_human)

        else:
            game.take_turn_ai(player_ai)

        game.print_board()

        winner = game.check_winner()

        if game.check_game_over(winner):
            break

        turn_human = not turn_human

    if winner is player_human:
        print("Human wins.")
        return HUMAN
    elif winner is player_ai:
        print("AI wins.")
        return AI
    elif winner is None:
        print("Tie.")
        return TIE


def play_game():
    tallies = {HUMAN: 0, AI: 0, TIE: 0}
    while True:
        winner = play_round()

        for outcome in OUTCOMES:
            if winner is outcome:
                tallies[outcome] += 1

        if not prompt_boolean("\nPlay again? (Y/n): "):
            print("\nHuman: {}\nAI:    {}\nTie:   {}"
                  .format(*[tallies[outcome] for outcome in OUTCOMES]))
            break


if __name__ == "__main__":
    play_game()
