#!../stracker/bin/python3
import numpy as np
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta

class Stockalyzer:
	def __init__(self, symbol, api, interval=tradeapi.TimeFrame.Hour, mode='store'):
		'''
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: ticker - 4 letter stock name eg. 'MSFT'
				interval='daily'
		'''

		# TODO: Auto adjust periods based on interval
		if interval == tradeapi.TimeFrame.Day:
			tpm = 1
		elif interval == tradeapi.TimeFrame.Hour:
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
		self.api = api
		self.account = self.api.get_account()
		self.interval = interval
		self.analysis = ''

		start = datetime.today().strftime('%Y-%m-%d')
		end = (datetime.today() - timedelta(365)).strftime('%Y-%m-%d')
		self.price_data = self.getPriceData(end, start, interval)
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
		self.avg_50 = self.price_data['close'].tail(50).mean()
		self.avg_200 = self.price_data['close'].tail(200).mean()

	def getPriceData(self, start, end, interval):
		return self.api.get_bars(self.stock, interval, start, end, adjustment='raw').df

	def getRSIData(self):
		# Relative Strength Indicator
		rsi_period = 7
		change = self.price_data['close'].diff()
		up = change.clip(lower=0)
		down = -1 * change.clip(upper=0)
		avgu = up.ewm(span=rsi_period, adjust=False).mean()
		avgd = down.ewm(span=rsi_period, adjust=False).mean()
		rs = avgu / avgd
		rsi = 100 - (100 / (1 + rs))
		return rsi

	def getStochData(self):
		# Stochastic oscillator
		low_d = self.price_data['low'].transform(lambda x: x.rolling(window=3).min())
		high_d = self.price_data['high'].transform(lambda x: x.rolling(window=3).max())
		low_k = self.price_data['low'].transform(lambda x: x.rolling(window=14).min())
		high_k = self.price_data['high'].transform(lambda x: x.rolling(window=14).max())

		stochd = ((self.price_data['close'] - low_d) / (high_d - low_d)) * 100
		stochk = ((self.price_data['close'] - low_k) / (high_k - low_k)) * 100
		stochd = stochd.rolling(window = 3).mean()
		stochk = stochk.rolling(window = 14).mean()
		return stochk, stochd

	def getMACDData(self):
		# Moving Average Convergence Divergence
		sema = self.price_data['close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
		lema = self.price_data['close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
		macd = sema - lema
		sig = macd.transform(lambda x: x.ewm(span=9, adjust=False).mean())
		return macd, sig

	def getADR(self):
		# Average Daily Range
		l = 7
		last_week = self.price_data.tail(l)
		daily_ranges = np.array([])
		for i in range(l):
			dr = last_week.iloc[i]['high'] - last_week.iloc[i]['low']
			hc = np.abs(last_week.iloc[i]['high'] - last_week.iloc[i]['close'])
			lc = np.abs(last_week.iloc[i]['high'] - last_week.iloc[i]['low'])
			m = np.array([dr, hc, lc]).max()
			daily_ranges = np.append(daily_ranges, m)
		adr = np.mean(daily_ranges)
		return adr

	def getPrice(self):
		return self.price_data['close'].iloc[-1]

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

	def getAnalysis(self, timestamp='now'):
		'''
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		'''
		if timestamp == 'now':
			rsi = self.rsi
			stoch = self.stochk
			macd = self.macd > self.macd_sig
		else:
			rsi = self.rsi_data.loc[timestamp]
			stoch = self.stochk_data.loc[timestamp]
			macd = self.macd_data.loc[timestamp] > self.macd_sig_data.loc[timestamp]

		if (rsi > 50 and
			stoch > 50 and
			macd and
			self.price > self.avg_50 and
			self.avg_50 > self.avg_200):
			return 'Buy'
		elif (rsi < 50 and
			stoch < 50 and
			macd and
			self.price < self.avg_50 and
			self.avg_50 < self.avg_200):
			return 'Sell'
		else:
			return 'Hold'