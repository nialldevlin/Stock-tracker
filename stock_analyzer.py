#!../stracker/bin/python3
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json

class Stockalyzer:
	def __init__(self, ticker, interval='daily', mode='store'):
		'''
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: ticker - 4 letter stock name eg. 'MSFT'
				interval='daily'
		'''
		if interval not in ('daily', '60min'):
			raise ValueError('interval must be daily or 60min')

		self.stock = ticker
		self.interval = interval
		self.analysis = ''
		self.ti = {}
		self.td = {}

		with open('apikey.txt', 'rb') as f:
			self.apikey = f.read()

		#TODO: Auto adjust periods based on interval
		if interval == 'daily':
			tpm = 1
		elif interval == '60min':
			tpm = 16
		self.params = {
			'RSI': {
				'interval':interval,
				'time_period':7 * tpm,
				'series_type':'close'
			},
			'STOCH': {
				'interval':interval,
				'fastkperiod':14 * tpm,
				'slowkperiod':3 * tpm,
				'slowdperiod':3 * tpm
			},
			'MACDEXT': {
				'interval':interval,
				'series_type':'close',
				'fastperiod':12 * tpm,
				'slowperiod':26 * tpm,
				'signalperiod':9 * tpm,
				'fastmatype':1,
				'slowmatype':1,
				'signalmatype':1
			},
			'ATR': {
				'interval':interval,
				'time_period':7 * tpm
			}

		}
		self.info = pd.DataFrame()
		self.history = pd.DataFrame()
		self.getLongData()


	# TODO: Make this better it sucks
	def getAnalysis(self):
		'''
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		'''
		return self.analysis
	
	def Wilder(self, data, periods):
		start = np.where(~np.isnan(data))[0][0] #Check if nans present in beginning
		Wilder = np.array([np.nan]*len(data))
		Wilder[start+periods-1] = data[start:(start+periods)].mean() #Simple Moving Average
		for i in range(start+periods,len(data)):
			Wilder[i] = (Wilder[i-1]*(periods-1) + data[i])/periods #Wilder Smoothing
		return(Wilder)
	
	def getLongData(self):
		ticker = yf.Ticker(self.stock)
		info = ticker.info
		important_data = [
			'fiftyDayAverage',
			'twoHundredDayAverage',
			'currentPrice',
			'trailingPE'
		]
		important_info = {}
		for i in info:
			if i in important_data:
				important_info[i] = info[i]
		self.history = pd.DataFrame(ticker.history(period='1y', interval='1d'))
		if 'currentPrice' not in important_info:
			important_info['currentPrice'] = self.history['Close'].tail(1)[0]

		self.td['price'] = self.history['Close']

		#Average Daily Range
		last_week = self.history.tail(7)
		daily_ranges = np.array([])
		for i in range(7):
			dr = last_week.iloc[i]['High'] - last_week.iloc[i]['Low']
			hc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Close'])
			lc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Low'])
			m = np.array([dr, hc, lc]).max()
			daily_ranges = np.append(daily_ranges, m)
		adr = np.mean(daily_ranges)
		self.ti['adr'] = adr

		#Stochastic oscillator
		low_d = self.history['Low'].transform(lambda x: x.rolling(window = 3).min())
		high_d = self.history['High'].transform(lambda x: x.rolling(window = 3).max())
		low_k = self.history['Low'].transform(lambda x: x.rolling(window = 14).min())
		high_k = self.history['High'].transform(lambda x: x.rolling(window = 14).max())

		stochd = ((self.history['Close'] - low_d)/(high_d - low_d))*100
		stochk = ((self.history['Close'] - low_k)/(high_k - low_k))*100

		self.td['stochd'] = stochd.rolling(window = 3).mean()
		self.td['stochk'] = stochk.rolling(window = 14).mean()

		#self.td['stoch ratio'] = self.td['stochd s']/self.td['stochd l']

		#Relative Strength Indicator
		rsi_period = 7
		change = self.history['Close'].diff()
		up = change.clip(lower=0)
		down = -1 * change.clip(upper=0)
		avgu = up.ewm(span=rsi_period, adjust=False).mean()
		avgd = down.ewm(span=rsi_period, adjust=False).mean()
		rs = avgu / avgd 
		self.td['rsi'] = 100 - (100/(1 + rs))
		
		#Moving Average Convergence Divergence
		sema = self.history['Close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
		lema = self.history['Close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
		self.td['macd'] = sema - lema
		self.td['signal'] = self.td['macd'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
		self.td = pd.DataFrame(self.td)

		rsi = self.td['rsi'].tail(1)[0]
		self.ti['rsi'] = rsi
		adr = self.ti['adr']
		price = important_info['currentPrice']
		self.ti['price'] = price
		stochd = self.td['stochd'].tail(1)[0]
		self.ti['stochd'] = stochd
		stochk = self.td['stochk'].tail(1)[0]
		stochk_d = self.td['stochk'].tail(2)[1] - self.td['stochk'].tail(2)[0]
		self.ti['stochk'] = stochk
		macd = self.td['macd'].tail(1)[0]
		self.ti['macd'] = macd
		sig = self.td['signal'].tail(1)[0]
		self.ti['sig'] = sig
		self.ti['sell price'] = price + 2 * adr
		self.ti['stop price'] = price - adr

		print(self.ti)
		if rsi > 50 and stochk > 50 and stochk_d > 0 and macd > sig:
			self.analysis = 'Rise'
		elif rsi < 50 and stochd < 50 and macd < sig:
			self.analysis = 'Fall'
		else:
			self.analysis = 'Hold'
	
	def getCurrentPrice():
		return self.ti['price']

	#TODO: Display all data
	def display(self):
		'''
		Displays graph of stock and averages with matplotlib
		'''

		if self.analysis == 'Rise':
			color = 'chartreuse'
		elif self.analysis == 'Fall':
			color = 'r'
		else:
			color = 'dimgray'
		fig, ax = plt.subplots(nrows=3)
		ax[0].axhline(y=self.ti['stop price'], color='r', label='Stop Price {:.2f}'.format(self.ti['stop price']))
		ax[0].axhline(y=self.ti['sell price'], color='chartreuse', label='Target Price{:.2f}'.format(self.ti['sell price']))
		ax[0].title.set_text('{} Stock Data: {} at {:.2f}'.format(self.stock, self.analysis, self.ti['price']))
		ax[0].legend(loc='upper left')
		ax[0].set_xlabel('Date')
		ax[0].set_ylabel('Price')
		ax[0].plot(self.td['price'], color=color, label='{} Price'.format(self.stock))
		ax[1].axhline(y=50)
		ax[1].legend(loc='upper left')
		ax[1].set_xlabel('Date')
		ax[1].set_ylabel('Value')
		ax[1].title.set_text('{} Technical Indicators - RSI: {}, Stochastic: {}'.format(self.stock, self.ti['rsi'], self.ti['stochk']))
		ax[1].plot(self.td[['rsi', 'stochk']])
		ax[2].title.set_text('{} MACD and Signal line'.format(self.stock, self.ti['macd'], self.ti['sig']))
		ax[2].legend(loc='upper left')
		ax[2].plot(self.td[['macd', 'signal']])
		plt.subplots_adjust(left=0.1,
                    bottom=0.1,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.4)
		plt.show()
		plt.clf()

	#TODO: FIX this too
	def saveAsPng(self, filename=''):
		'''
		Saves graph as png to filename
		If none specified, defaults to {stock}.png
		'''
		f = filename
		if f == '':
			f = '{}.png'.format(self.stock)
		hist = self.getPriceData()[::-1]
		if self.analysis == 'Rise':
			color = 'chartreuse'
		elif self.analysis == 'Fall':
			color = 'r'
		else:
			color = 'dimgray'
		fig, ax = plt.subplots(nrows=3)
		ax[0].axhline(y=self.ti['stop price'], color='r', label='Stop Price {:.2f}'.format(self.ti['stop price']))
		ax[0].axhline(y=self.ti['sell price'], color='chartreuse', label='Target Price{:.2f}'.format(self.ti['sell price']))
		ax[0].title.set_text('{} Stock Data: {} at {:.2f}'.format(self.stock, self.analysis, self.ti['price']))
		ax[0].legend(loc='upper left')
		ax[0].set_xlabel('Date')
		ax[0].set_ylabel('Price')
		ax[0].plot(self.td['price'], color=color, label='{} Price'.format(self.stock))
		ax[1].axhline(y=50)
		ax[1].legend(loc='upper left')
		ax[1].set_xlabel('Date')
		ax[1].set_ylabel('Value')
		ax[1].title.set_text('{} Technical Indicators - RSI: {}, Stochastic: {}'.format(self.stock, self.ti['rsi'], self.ti['stochk']))
		ax[1].plot(self.td[['rsi', 'stochk']])
		ax[2].title.set_text('{} MACD and Signal line'.format(self.stock, self.ti['macd'], self.ti['sig']))
		ax[2].legend(loc='upper left')
		ax[2].plot(self.td[['macd', 'signal']])
		plt.subplots_adjust(left=0.1,
                    bottom=0.9,
                    right=0.9,
                    top=0.9,
                    wspace=0.4,
                    hspace=0.4)
		plt.savefig(f)
		plt.clf()
