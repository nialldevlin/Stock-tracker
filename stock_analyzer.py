#!../stracker/bin/python3
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json

class Stockalyzer:
	def __init__(self, symbol, interval='daily', mode='store'):
		'''
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: ticker - 4 letter stock name eg. 'MSFT'
				interval='daily'
		'''
		if interval not in ('daily', '60min'):
			raise ValueError('interval must be daily or 60min')

		# TODO: Auto adjust periods based on interval
		if interval == 'daily':
			tpm = 1
		elif interval == '60min':
			tpm = 16

		self.params = {
			'RSI': {
				'interval': interval,
				'time_period': 7 * tpm,
				'series_type': 'close'
			},
			'STOCH': {
				'interval': interval,
				'fastkperiod': 14 * tpm,
				'slowkperiod': 3 * tpm,
				'slowdperiod': 3 * tpm
			},
			'MACDEXT': {
				'interval': interval,
				'series_type': 'close',
				'fastperiod': 12 * tpm,
				'slowperiod': 26 * tpm,
				'signalperiod': 9 * tpm,
				'fastmatype': 1,
				'slowmatype': 1,
				'signalmatype': 1
			},
			'ATR': {
				'interval': interval,
				'time_period': 7 * tpm
			}
		}

		self.stock = symbol
		self.ticker = yf.Ticker(self.stock)
		self.interval = interval
		self.analysis = ''
		self.ti = {}
		self.td = {}

		self.price_data = self.getPriceData()
		self.rsi_data = self.getRSIData()
		self.stochk_data, self.stochd_data = self.getStochData()
		self.macd_data, self.macd_sig_data = self.getMACDData()

		self.price = self.getPrice()
		self.rsi = self.getRSI()
		self.stochk, self.stochd = self.getStoch()
		self.macd, self.macd_sig = self.getMACD()
		self.adr = self.getADR()
		self.stop = self.price - self.adr
		self.sell = self.price + self.adr * 2

	def getPriceData(self):
		return pd.DataFrame(self.ticker.history(period='1y', interval='1d'))

	def getRSIData(self):
		# Relative Strength Indicator
		rsi_period = 7
		change = self.price_data['Close'].diff()
		up = change.clip(lower=0)
		down = -1 * change.clip(upper=0)
		avgu = up.ewm(span=rsi_period, adjust=False).mean()
		avgd = down.ewm(span=rsi_period, adjust=False).mean()
		rs = avgu / avgd
		rsi = 100 - (100 / (1 + rs))
		return rsi

	def getStochData(self):
		# Stochastic oscillator
		low_d = self.price_data['Low'].transform(lambda x: x.rolling(window=3).min())
		high_d = self.price_data['High'].transform(lambda x: x.rolling(window=3).max())
		low_k = self.price_data['Low'].transform(lambda x: x.rolling(window=14).min())
		high_k = self.price_data['High'].transform(lambda x: x.rolling(window=14).max())

		stochd = ((self.price_data['Close'] - low_d) / (high_d - low_d)) * 100
		stochk = ((self.price_data['Close'] - low_k) / (high_k - low_k)) * 100
		stochd = stochd.rolling(window = 3).mean()
		stochk = stochk.rolling(window = 14).mean()
		return stochk, stochd

	def getMACDData(self):
		# Moving Average Convergence Divergence
		sema = self.price_data['Close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
		lema = self.price_data['Close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
		macd = sema - lema
		sig = macd.transform(lambda x: x.ewm(span=9, adjust=False).mean())
		return macd, sig

	def getADR(self):
		# Average Daily Range
		l = 7
		last_week = self.price_data.tail(l)
		daily_ranges = np.array([])
		for i in range(l):
			dr = last_week.iloc[i]['High'] - last_week.iloc[i]['Low']
			hc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Close'])
			lc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Low'])
			m = np.array([dr, hc, lc]).max()
			daily_ranges = np.append(daily_ranges, m)
		adr = np.mean(daily_ranges)
		return adr

	def getPrice(self):
		return self.price_data['Close'].iloc[-1]

	def getRSI(self):
		return self.rsi_data[-1]

	def getStoch(self):
		return self.stochk_data[-1], self.stochd_data[-1]

	def getMACD(self):
		return self.macd_data[-1], self.macd_sig_data[-1]

	def getStopPrice(self):
		return self.stop

	def getSellPrice(self):
		return self.sell

	def getAnalysis(self):
		'''
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		'''
		if self.rsi > 50 and self.stochk > 50 and self.macd > self.macd_sig:
			return 'Buy'
		elif self.rsi < 50 and self.stochk < 50 and self.macd < self.macd_sig:
			return 'Sell'
		else:
			return 'Hold'
"""
	def display(self, filename=''):
		'''
		Displays graph of stock and averages with matplotlib
		'''

		if self.analysis == 'Rise':
			color = 'chartreuse'
		elif self.analysis == 'Fall':
			color = 'r'
		else:
			color = 'dimgray'
		fig, ax = plt.subplots(nrows=3, figsize=(6, 6))
		ax[0].axhline(y=self.ti['stop price'], color='r', label='Stop Price {:.2f}'.format(self.ti['stop price']))
		ax[0].axhline(y=self.ti['sell price'], color='chartreuse', label='Target Price{:.2f}'.format(self.ti['sell price']))
		ax[0].title.set_text('{} Stock Data: {} at {:.2f}'.format(self.stock, self.analysis, self.ti['price']))
		ax[0].legend(loc='upper left')
		ax[0].set_xlabel('Date')
		ax[0].set_ylabel('Price')
		ax[0].plot(self.td['price'], color=color, label='{} Price'.format(self.stock))
		ax[1].axhline(y=50)
		ax[1].set_xlabel('Date')
		ax[1].set_ylabel('Value')
		ax[1].title.set_text('{} Technical Indicators - RSI, Stochastic'.format(self.stock, self.ti['rsi'], self.ti['stochk']))
		ax[1].plot(self.td['rsi'], label='RSI {:.2f}'.format(self.ti['rsi']))
		ax[1].plot(self.td['stochk'], label='Stochastic Long {:.2f}'.format(self.ti['stochk']))
		ax[1].plot(self.td['stochd'], label='Stochastic Short {:.2f}'.format(self.ti['stochd']))
		ax[1].legend(loc='upper left')
		ax[2].title.set_text('{} MACD and Signal line'.format(self.stock, self.ti['macd'], self.ti['sig']))
		ax[2].plot(self.td['macd'], label='MACD {:.2f}'.format(self.ti['macd']))
		ax[2].plot(self.td['signal'], label='Signal {:.2f}'.format(self.ti['sig']))
		ax[2].legend(loc='upper left')
		fig.tight_layout()
		if filename:
			plt.savefig(filename)
		else:
			plt.show()
		plt.clf()"""