"""This file plays tetris."""
import os
import time

import keras
from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, InputLayer

from MaTris import matris

import autoplay as autop
import utils


def play():

    if os.path.exists('tetris.model'):
        model = keras.models.load_model('tetris.model')
        print("Loaded model from disk")
    else:
        model = Sequential()
        model.add(InputLayer(batch_input_shape=(224, 1)))
        model.add(Dense(100, activation='sigmoid'))
        model.add(Dense(100, activation='sigmoid'))
        model.add(Dense(5, activation='linear'))
        model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    autoplay = autop.Autoplay(model=model, verbose=True, graphics=False, speedup=True)

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

    print("Save model to disk")
    model.save('tetris.model')

    print("Done!")


if __name__ == "__main__":
    play()
