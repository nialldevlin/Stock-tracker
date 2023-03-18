import numpy as np
import pandas as pd

"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'
os.environ["TF_CPP_MIN_VLOG_LEVEL"] = '1'
os.environ["TF_DUMP_GRAPH_PREFIX"] = '../tf'
"""

import tensorflow as tf
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from tqdm import tqdm
from ai_spider import AISpider

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

s = AISpider()

print("Create model")
model = Sequential()
model.add(LSTM(units=60,
    return_sequences=True,
    input_shape=(s.f_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=60, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=60, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=60, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=60))
model.add(Dropout(0.2))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mean_squared_error')

print("Train model")
model.fit(s.f_train, s.l_train, epochs=100, batch_size=128, validation_split=0.1)
model.save('../data/model.h5')

print("Evaluate on test data")
results = model.evaluate(s.f_test, s.l_test, batch_size=32)
print("test loss, test acc:", results)


