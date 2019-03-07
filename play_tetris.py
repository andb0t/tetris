"""This file plays tetris."""
import os
import random
import time

from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, InputLayer

from MaTris import matris, tetrominoes

import utils


tetromino_colors = sorted([x[0] for x in tetrominoes.tetrominoes.values()])


class Autoplay():
    def __init__(self, model=None, verbose=False, graphics=True, speedup=False):
        self.verbose = verbose
        self.graphics = graphics
        self.speedup = speedup
        self.model = model
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
        self.state = None

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
        self.train()
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
        self.state = state

    def train(self):
        prediction = self.model.predict(self.state)
        print("This prediction:", prediction)
        print("This prediction:", len(prediction))

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
            print("- State dimension:", len(self.state))
            print("- Occupied matrix fields: %d" % len(matrix_occupied))
            # print(matrix_occupied)
            print("Current tetromino:", self.current_tetromino)
            print("- Rotation:", self.tetromino_rotation)
            print("- Position:", self.tetromino_position)
            print("Next tetromino:", self.next_tetromino)
            print("-----------------")
            print()


def play():

    if os.path.exists('model.json'):
        # load json and create model
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights("model.h5")
        print("Loaded model from disk")
    else:
        model = Sequential()
        model.add(InputLayer(batch_input_shape=(224, 1)))
        model.add(Dense(100, activation='sigmoid'))
        model.add(Dense(100, activation='sigmoid'))
        model.add(Dense(5, activation='linear'))
        model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    autoplay = Autoplay(model=model, verbose=True, graphics=False, speedup=True)

    print("Start!")
    num_episodes = 10
    try:
        for i in range(num_episodes):
            start_time = time.time()
            if autoplay.verbose:
                matris.start_game(autoplay)
            else:
                with utils.suppress_stdout_stderr():
                    matris.start_game(autoplay)
            stop_time = time.time()
            print("{2}. Tetris game finished!\tScore: {0}\tTime (s): {1:.3f}".format(autoplay.score,
                                                                                     stop_time - start_time,
                                                                                     i+1))
    except KeyboardInterrupt:
        print("End!")

    # serialize model to JSON
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model.h5")
    print("Saved model to disk")


if __name__ == "__main__":
    play()
