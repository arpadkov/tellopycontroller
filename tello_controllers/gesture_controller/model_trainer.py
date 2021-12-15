from tello_controllers.gesture_controller.gesture_data.gestures import Gesture

from PyQt5 import QtWidgets, QtCore

import os
import numpy as np
import tensorflow as tf


class GestureModelTrainer(QtCore.QThread):

    training_finished = QtCore.pyqtSignal()

    def __init__(self, gesture_dataset_dir, keras_model_dir):
        super(GestureModelTrainer, self).__init__()

        self.gesture_dataset_dir = gesture_dataset_dir

        self.keras_model_dir = keras_model_dir

        # self.dataset_dir = os.path.join(os.path.dirname(os.getcwd()), 'gesture_data')

        self.output_shape = len(Gesture)

        self.x_train = np.empty((0,84), float)
        self.y_train = np.empty((0,), int)

    def read_training_data(self):

        for filename in os.listdir(self.gesture_dataset_dir):
            if '.csv' in filename:

                csv_file = os.path.join(self.gesture_dataset_dir, filename)

                x_train_temp = np.loadtxt(csv_file, delimiter=',', dtype='float32', usecols=list(range(1, 84 + 1)))
                y_train_temp = np.loadtxt(csv_file, delimiter=',', dtype='int32', usecols=0)

                self.x_train = np.append(self.x_train, x_train_temp, axis=0)
                self.y_train = np.append(self.y_train, y_train_temp, axis=0)

    def build_model(self):

        inputs = tf.keras.Input(shape=(84,))
        x = tf.keras.layers.Dense(640, activation=tf.nn.relu)(inputs)
        x = tf.keras.layers.Dense(640, activation="relu", name="dense_2")(x)
        outputs = tf.keras.layers.Dense(self.output_shape, activation=tf.nn.softmax)(x)

        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)

    def compile_model(self):

        self.model.compile(
            optimizer=tf.keras.optimizers.RMSprop(),  # Optimizer
            # Loss function to minimize
            loss=tf.keras.losses.SparseCategoricalCrossentropy(),
            # List of metrics to monitor
            metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
        )

    def fit_model(self):
        self.model.fit(
            self.x_train,
            self.y_train,
            batch_size=64,
            epochs=10,
        )

    def save_model(self):

        self.read_training_data()
        self.build_model()
        self.compile_model()
        self.fit_model()

        self.model.save(self.keras_model_dir)

    def run(self):
        self.save_model()
        self.training_finished.emit()
