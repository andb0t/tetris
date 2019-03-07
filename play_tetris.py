"""This file plays tetris."""
import random

from MaTris import matris


class Autoplay():
    def __init__(self):
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

    def log(self, matrix, current_tetromino, next_tetromino, tetromino_rotation, tetromino_position, score):
        self.stepcount += 1
        self.matrix = matrix
        self.current_tetromino = current_tetromino
        self.next_tetromino = next_tetromino
        self.tetromino_rotation = tetromino_rotation
        self.tetromino_position = tetromino_position
        self.score = score
        self.print()

    def decide(self):
        decision = random.randint(0, 4)
        self.k_up = decision == 0
        self.k_down = decision == 1
        self.k_right = decision == 2
        self.k_left = decision == 3
        self.k_space = decision == 4
        self.k_pass = not any([self.k_up, self.k_down, self.k_right, self.k_left, self.k_space])

    def print(self, verbose=False):
        print("%d.:" % self.stepcount)
        if verbose:
            print("Game info:")
            print("- Score:", self.score)
            print("Matrix occupied:")
            print([entry for entry in self.matrix if self.matrix[entry]])
            print("Current tetromino")
            print("- Shape:", self.current_tetromino.shape)
            print("- Rotation:", self.tetromino_rotation)
            print("- Position:", self.tetromino_position)
            print("Next tetromino")
            print("- Shape:", self.next_tetromino.shape)
            print()
            print("-----------------")
            print()


def play():
    autoplay = Autoplay()
    print("Start!")
    matris.start_game(autoplay)
    print("End!")


if __name__ == "__main__":
    play()
