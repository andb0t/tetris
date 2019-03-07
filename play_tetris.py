"""This file plays tetris."""
import argparse
import os
import time

import keras
from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense, InputLayer
from keras.utils import plot_model
import psutil

from MaTris import matris

import autoplay as autop
import utils


parser = argparse.ArgumentParser()
parser.add_argument("--train", help='train the model', action='store_true')
parser.add_argument("--new", help='overwrite old model', action='store_true')
parser.add_argument("--verbose", help='verbose output', action='store_true')
parser.add_argument("--graphics", help='show graphics', action='store_true')
parser.add_argument("--noai", help='don\'t use AI model', action='store_true')
args = parser.parse_args()


def play():

    env_display = os.environ["DISPLAY"]
    if not args.graphics:
        print("Disable display ...")
        os.environ["DISPLAY"] = ":99"
        if "Xvfb" not in (p.name() for p in psutil.process_iter()):
            print("Starting Xvfb service on display port :99 ...")
            os.system("Xvfb :99 &")

    if args.noai:
        model = None
    else:
        if not args.new and os.path.exists('tetris.model'):
            model = keras.models.load_model('tetris.model')
            print("Loaded model from disk")
        else:
            model = Sequential()
            model.add(Dense(100, input_shape=(224,), activation='relu'))
            model.add(Dense(100, activation='relu'))
            model.add(Dense(6))  # number of actions
            model.compile(loss='mse', optimizer='adam', metrics=['mae'])
        print(model.summary())
        plot_model(model, show_shapes=True, to_file='model.png')

    autoplay = autop.Autoplay(model=model, verbose=args.verbose, training=args.train,
                              graphics=False, speedup=True)

    print("Start!")
    num_episodes = 1000
    try:
        for i in range(num_episodes):
            start_time = time.time()
            if args.verbose:
                matris.start_game(autoplay)
            else:
                with utils.suppress_stdout_stderr():
                    matris.start_game(autoplay)
            stop_time = time.time()
            print("{2}. Tetris game finished!\tScore: {0}\tTime (s): {1:.1f}\tLoss: {3}".
                  format(autoplay.score,
                         stop_time - start_time,
                         i+1,
                         autoplay.loss))
    except KeyboardInterrupt:
        print("Interrupt games!")

    if args.train:
        model.save('tetris.model')
        print("Saved model to disk")

    if not args.graphics:
        print("Reset display ...")
        os.environ["DISPLAY"] = env_display

    print("Done!")


if __name__ == "__main__":
    play()
