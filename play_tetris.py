"""This file plays tetris."""
import random

from MaTris import matris, tetrominoes

import utils


tetromino_colors = sorted([x[0] for x in tetrominoes.tetrominoes.values()])


class Autoplay():
    def __init__(self, verbose=False, graphics=True, speedup=False):
        self.k_up = False
        self.k_down = False
        self.k_right = False
        self.k_left = False
        self.k_space = False
        self.k_pass = False
        self.stepcount = 0
        self.matrix = None
        self.current_tetromino = None
        self.next_tetromino = None
        self.tetromino_rotation = None
        self.tetromino_position = None
        self.score = 0
        self.sorted_keys = None
        self.verbose = verbose
        self.graphics = graphics
        self.speedup = speedup

    def record(self, matrix, current_tetromino, next_tetromino, tetromino_rotation, tetromino_position, score):
        self.stepcount += 1
        self.matrix = matrix
        self.current_tetromino = utils.index_in_list(current_tetromino[0], tetromino_colors)
        self.next_tetromino = utils.index_in_list(next_tetromino[0], tetromino_colors)
        self.tetromino_rotation = tetromino_rotation
        self.tetromino_position = tetromino_position
        self.score = score
        if not self.sorted_keys:
            self.sorted_keys = sorted(self.matrix.keys())
        self.log()
        self.print()

    def log(self):
        state = []
        # insert locked blocks
        for key in self.sorted_keys:
            state.append(1 if self.matrix[key] else 0)
        # insert current tetromino
        state.append(self.current_tetromino)
        state.append(self.tetromino_rotation)
        # insert current tetromino position
        # encode as index of its position - maybe better to encode it as one hot vector?
        state.append(utils.index_in_list(self.tetromino_position, self.sorted_keys))
        # insert next tetromino
        state.append(self.next_tetromino)

    def decide(self):
        decision = random.randint(0, 4)
        self.k_up = decision == 0
        self.k_down = decision == 1
        self.k_right = decision == 2
        self.k_left = decision == 3
        self.k_space = decision == 4
        self.k_pass = not any([self.k_up, self.k_down, self.k_right, self.k_left, self.k_space])

    def print(self):
        if self.verbose:
            print("%d.:" % self.stepcount)
            matrix_occupied = [entry for entry in self.matrix if self.matrix[entry]]
            print("Game info:")
            print("- Score:", self.score)
            print("- Occupied matrix fields: %d" % len(matrix_occupied))
            # print(matrix_occupied)
            print("Current tetromino:", self.current_tetromino)
            print("- Rotation:", self.tetromino_rotation)
            print("- Position:", self.tetromino_position)
            print("Next tetromino:", self.next_tetromino)
            print("-----------------")
            print()


def play():
    autoplay = Autoplay(verbose=False, graphics=False, speedup=True)
    while True:
        print("Start!")
        with utils.suppress_stdout_stderr():
            matris.start_game(autoplay)
        print("End!")
        print("Final score:", autoplay.score)


if __name__ == "__main__":
    play()
