from tellopycontroller.gesture_data.gestures import Gesture

import os
import numpy as np
import tensorflow as tf

model_file = os.path.join(os.path.dirname(os.getcwd()), 'keras_gesture_model')

dataset_dir = os.path.join(os.path.dirname(os.getcwd()), 'gesture_data')

output_shape = len(Gesture)

x_train = np.empty((0,84), float)
y_train = np.empty((0,), int)

for filename in os.listdir(dataset_dir):
    if '.csv' in filename:

        csv_file = os.path.join(dataset_dir, filename)

        x_train_temp = np.loadtxt(csv_file, delimiter=',', dtype='float32', usecols=list(range(1, (42 * 2) + 1)))
        y_train_temp = np.loadtxt(csv_file, delimiter=',', dtype='int32', usecols=(0))

        x_train = np.append(x_train, x_train_temp, axis=0)
        y_train = np.append(y_train, y_train_temp, axis=0)


inputs = tf.keras.Input(shape=(84,))
x = tf.keras.layers.Dense(640, activation=tf.nn.relu)(inputs)
x = tf.keras.layers.Dense(640, activation="relu", name="dense_2")(x)
outputs = tf.keras.layers.Dense(output_shape, activation=tf.nn.softmax)(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

model.compile(
    optimizer=tf.keras.optimizers.RMSprop(),  # Optimizer
    # Loss function to minimize
    loss=tf.keras.losses.SparseCategoricalCrossentropy(),
    # List of metrics to monitor
    metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
)


history = model.fit(
    x_train,
    y_train,
    batch_size=64,
    epochs=10,
)

model.save(model_file)
