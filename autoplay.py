"""The class to play the tetris game without intervention."""
import random

import numpy as np

from MaTris import tetrominoes

import utils


tetromino_colors = sorted([x[0] for x in tetrominoes.tetrominoes.values()])


class Autoplay():
    def __init__(self, model=None, verbose=False, graphics=True, speedup=False, training=False):
        self.verbose = verbose
        self.graphics = graphics
        self.speedup = speedup
        self.model = model
        self.training = training
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
        self.old_state = None
        self.memory = []
        self.max_memory = 10
        self.decision = None
        self.loss = 0

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
        self.old_state = self.state
        self.state = np.array(state).reshape(1, len(state))
        self.memory.append(self.state)
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def get_batch(self):
        batch_size = 50
        discount = 0.9
        len_memory = len(self.memory)
        num_actions = self.model.output_shape[-1]
        env_dim = self.state.shape[1]
        inputs = np.zeros((min(len_memory, batch_size), env_dim))
        targets = np.zeros((inputs.shape[0], num_actions))
        for i in np.random.randint(0, len_memory, size=inputs.shape[0]):
            inputs[i:i+1] = self.old_state
            # There should be no target values for actions not taken.
            # Thou shalt not correct actions not taken #deep
            new_prediction = self.model.predict(self.state, steps=inputs.shape[0])
            q_sa = np.max(new_prediction[0])
            if self.old_state is not None:
                targets[i] = self.model.predict(self.old_state, steps=inputs.shape[0])[0]
            else:
                targets[i] = new_prediction
            # reward_t + gamma * max_a' Q(s', a')
            index = targets.shape[1]-1 if not self.decision else min(self.decision, targets.shape[1]-1)
            targets[i, index] = self.score + discount * q_sa
        return inputs, targets

    def train(self):
        if not self.model or not self.training:
            return
        inputs, targets = self.get_batch()
        self.loss += self.model.train_on_batch(inputs, targets)[0]

    def decide(self):
        exploration_probability = 0.3
        # get next action
        if not self.model or np.random.rand() <= exploration_probability:
            self.decision = random.randint(0, 5)
        else:
            actions = self.model.predict(self.state)
            self.decision = np.argmax(actions)
        # apply action to game
        self.k_up = self.decision == 0
        self.k_down = self.decision == 1
        self.k_right = self.decision == 2
        self.k_left = self.decision == 3
        self.k_space = self.decision == 4
        self.k_pass = self.decision == 5

    def print(self):
        if self.verbose:
            print("%d.:" % self.stepcount)
            matrix_occupied = [entry for entry in self.matrix if self.matrix[entry]]
            print("Game info:")
            print("- Score:", self.score)
            print("- State dimension:", len(self.state))
            print("- Occupied matrix fields: %d" % len(matrix_occupied))
            if self.decision is not None:
                print("Last decision:", self.decision)
            # print(matrix_occupied)
            print("Current tetromino:", self.current_tetromino)
            print("- Rotation:", self.tetromino_rotation)
            print("- Position:", self.tetromino_position)
            print("Next tetromino:", self.next_tetromino)
            print("-----------------")
            print()
