import tensorflow as tf
from tensorflow import keras
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from ai_spider import AISpider
from sklearn.preprocessing import MinMaxScaler
import warnings

os.environ["TF_CPP_MIN_VLOG_LEVEL"] = '2'
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

class AIPredict(AISpider):
    def __init__(self, model_path, n_data_points, tickers, test=False):
        super().__init__(period='1y', tickers=tickers)
        self.model = keras.models.load_model(model_path)
        self.ndp = n_data_points
        self.predictions = self.predict()

    def predict(self):
        p_data = self.data.iloc[-1*self.ndp:]
        p_data = p_data.interpolate()
        p_data = p_data.dropna(axis=1)
        self.tickers = p_data.columns.values.tolist()
        scaler = MinMaxScaler(feature_range = (0, 1))
        p_data = scaler.fit_transform(p_data.values).transpose()
        p_data = np.reshape(p_data, (p_data.shape[0], p_data.shape[1], 1))
        preds = self.model.predict(p_data) * 100
        return pd.DataFrame(preds.transpose(), columns=self.tickers)

    def test(self, ticker):
        p_data = self.data[ticker]
    
    def visualize(self, ticker):
        pred = self.predictions[ticker].values[0]
        c = 'r' if pred < 0 else 'g'
        plt.plot(self.data[ticker], color=c)
        plt.ylabel('Price')
        plt.title('{} - Score: {}%'.format(ticker, pred))
        plt.show()

    def getBest(self, num):
        s = self.predictions.sort_values(axis=1, by=0, ascending=False)
        return s.iloc[:, :num]

    def getWorst(self, num):
        s = self.predictions.sort_values(axis=1, by=0, ascending=True)
        return s.iloc[:, :num]


