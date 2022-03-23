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

#########################################################
# Below here is legacy code
#########################################################
'''
	def LongShortAvgAnalysis(self, dataset):
		
		If short term average is above long term average by
		pgd, stock is rising. Send buy signal until difference
		is above pgd + sda. If short term average is below long term
		average by same criteria, send sell signal While stock
		is rising/falling and buy/sell signal is over, send
		hold signal.
		Params: dataset to analyze
		Return: string 'Buy', 'Sell', or 'Hold'
		
		short_avg = dataset[-1 * self.short_avg:].mean()
		long_avg = dataset[-1 * self.long_avg:].mean()
		current_price = self.getCurrentPrice()
		if short_avg - long_avg > (self.pgd * current_price) and short_avg - long_avg < (self.pgd * current_price) + self.sda:
			self.analysis = 'Buy'
			return 'Buy'
		elif long_avg - short_avg > (self.pgd * current_price) and long_avg - short_avg < (self.pgd * current_price) + self.sda:
			self.analysis = 'Sell'
			return 'Sell'
		self.analysis = 'Hold'
		return 'Hold'

	def runSimulationLS(self, startingBalance, buyAmount, startingStock=0, verbose=False):
		
		Runs simulation on stock history. Analysis is run on stock data to a certain date
		Starts with given balance and starting stock (default 0) and invests based on
		analysis.
		Params: startingbalance - amount to start with in $
				buyAmount - amount of stock to buy each time
				startingStock - amount of stock to start with
		Return: ending balance, number of stock
		
		balance = startingBalance
		ba = buyAmount
		num_stock = startingStock
		data = self.getStockData().values
		last_transaction = ''
		last_price = 0
		printHold = False;
		for i in range(self.short_avg, data.size):
			data_slice = data[:i]
			if len(data_slice) > self.short_avg:
				current_price = data_slice[-1]
				analysis = self.tiaanalysis(data_slice)
				if analysis == 'Buy' and last_transaction != 'Buy':
					if ba * current_price <= balance:
						balance -= ba * current_price
						num_stock += ba
						last_transaction = 'Buy'
						if verbose:
							print('Bought {} of {} at {:.2f}'.format(ba, self.stock, current_price))
					else:
						if verbose:
							print('Not Bought {} of {} at {:.2f}'.format(ba, self.stock, current_price))
				elif analysis == 'Sell' and last_transaction != 'Sell':
					if num_stock >= ba:
						balance += ba * current_price
						num_stock -= ba
						last_transaction = 'Sell'
						if verbose:
							print('Sold {} of {} at {:.2f}'.format(ba, self.stock, current_price))
					else:
						if verbose:
							print('Not Sold {} of {} at {:.2f}'.format(ba, self.stock, current_price))
				else:
					if verbose:
						if printHold:
							print('Hold {} at {:.2f}'.format(self.stock, current_price))
		return balance, num_stock
	def tiaanalysis(self, date='now'):
	
		Current stock price is compared to short term std
		of dataset.
		Params: dataset to analyze
		Return: dictionary of
			analysis - 'Rise', 'Fall', or 'Hold'
			current price - price of stock
			stop price - price to sell at to cut losses
			sell price - target price to sell at
		

		# Get date
		# Isolate wanted technical indicators from downloaded data
		if date == 'now':
			current_price = float(self.price_data['1. open'].iloc[0])
			rsi = float(self.rsi_data.iloc[0])			
			stochk = float(self.stoch_data['SlowK'].iloc[0])
			stochd = float(self.stoch_data['SlowD'].iloc[0])
			macd = float(self.macd_data['MACD'].iloc[0])
			macd_sig = float(self.macd_data['MACD_Signal'].iloc[0])
			adr = float(self.adr_data.iloc[0])
		else:
			c_date = date + ':00'
			print(c_date)
			current_price = float(self.price_data['1. open'][c_date])
			rsi = float(self.rsi_data[date])			
			stochk = float(self.stoch_data['SlowK'][date])
			stochd = float(self.stoch_data['SlowD'][date])
			macd = float(self.macd_data['MACD'][date])
			macd_sig = float(self.macd_data['MACD_Signal'][date])
			adr = float(self.adr_data[date])

		# Use indicators to determine rising or falling
		# If not all agree, in a hold position
		if rsi > 50 and stochk > 50 and stochd > 50 and macd > macd_sig:
			self.analysis = 'Rise'
		elif rsi < 50 and stochk < 50 and stochd < 50 and macd < macd_sig:
			self.analysis = 'Fall'
		else:
			self.analysis = 'Hold'

		stop_price = current_price - adr
		sell_price = current_price + 2 * adr
		out = {
			'analysis':self.analysis,
			'current price':current_price,
			'stop price':stop_price,
			'sell price':sell_price
		}

		return out

	def runSimulationTI(self, startingBalance, buyAmount, days=100, startingStock=0, verbose=False):
		balance = startingBalance
		ba = buyAmount
		num_stock = startingStock
		last_analysis = ''
		current_analysis = ''
		printHold = False;
		stop_price = 0
		sell_price = 0
		for i in range(1, days+1):
			curr_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
			data = self.tiaanalysis(curr_date, 'read')
			if (data['analysis'] != 'fail'):
				last_analysis = analysis
				current_analysis = data['analysis']
				current_price = data['current price']

				
				If changes to buy:
					buy if able
					log stop/sell price
				if changes to sell or hits stop/sell price:
					sell if able

				

				if current_analysis == 'Rise' and last_analysis != 'Rise':
					if ba * current_price <= balance:
						balance -= ba * current_price
						num_stock += ba
						last_transaction = 'Buy'
						stop_price = data['stop price']
						sell_price = data['sell price']
						if verbose:
							print('Bought {} of {} at {:.2f}'.format(ba, self.stock, current_price))
					else:
						if verbose:
							print('Not Bought {} of {} at {:.2f}'.format(ba, self.stock, current_price))
				elif (analysis == 'Sell' and last_transaction != 'Sell') or current_price < stop_price or current_price > sell_price:
					if num_stock >= ba:
						balance += ba * current_price
						num_stock -= ba
						last_transaction = 'Sell'

if verbose:
							print('Sold {} of {} at {:.2f}'.format(ba, self.stock, current_price))
					else:
						if verbose:
							print('Not Sold {} of {} at {:.2f}'.format(ba, self.stock, current_price))
				else:
					if verbose:
						if printHold:
							print('Hold {} at {:.2f}'.format(self.stock, current_price))
		return balance, num_stock

	def getTechnicalIndicators(self, mode='live'):
		# API request strings
		if self.interval == 'daily':
			price_str = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}'.format(
				self.stock,
				self.apikey
			)
		else:
			price_str = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&outputsize=full&interval=60min&apikey={}'.format(
				self.stock,
				self.apikey
			)

		rsi_str = 'https://www.alphavantage.co/query?function=RSI&symbol={}&interval={}&time_period={}&series_type={}&apikey={}'.format(
			self.stock,
			self.params['RSI']['interval'],
			self.params['RSI']['time_period'],
			self.params['RSI']['series_type'],
			self.apikey
		)

		stoch_str = 'https://www.alphavantage.co/query?function=STOCH&symbol={}&interval={}&fastkperiod={}&slowkperiod={}&slowdperiod={}&apikey={}'.format(
			self.stock,
			self.params['STOCH']['interval'],
			self.params['STOCH']['fastkperiod'],
			self.params['STOCH']['slowkperiod'],
			self.params['STOCH']['slowdperiod'],
			self.apikey
		)

		macdext_str = 'https://www.alphavantage.co/query?function=MACDEXT&symbol={}&interval={}&series_type={}&fastmatype={}&slowmatype={}&signalmatype={}&apikey={}'.format(
			self.stock,
			self.params['MACDEXT']['interval'],
			self.params['MACDEXT']['series_type'],
			self.params['MACDEXT']['fastmatype'],
			self.params['MACDEXT']['slowmatype'],
			self.params['MACDEXT']['signalmatype'],
			self.apikey
		)

		adr_str = 'https://www.alphavantage.co/query?function=ATR&symbol={}&interval={}&time_period={}&apikey={}'.format(
			self.stock,
			self.params['ATR']['interval'],
			self.params['RSI']['time_period'],
			self.apikey
		)
		# Get technical indicators
		# Able to get stored data for testing without using api calls
		if mode == 'store':
			self.price_data = requests.get(price_str).json()
			with open('price_{}.json'.format(self.stock), 'w') as f:
				json.dump(self.price_data, f)

			self.rsi_data = requests.get(rsi_str).json()
			with open('rsi_{}.json'.format(self.stock), 'w') as f:
				json.dump(self.rsi_data, f)

			self.stoch_data = requests.get(stoch_str).json()
			with open('stoch_{}.json'.format(self.stock), 'w') as f:
				json.dump(self.stoch_data, f)

			self.macd_data = requests.get(macdext_str).json()
			with open('macd_{}.json'.format(self.stock), 'w') as f:
				json.dump(self.macd_data, f)

			self.adr_data = requests.get(adr_str).json()
			with open('adr_{}.json'.format(self.stock), 'w') as f:
				json.dump(self.adr_data, f)
		elif mode == 'read':
			with open('price_{}.json'.format(self.stock), 'r') as f:
				self.price_data = json.load(f)

			with open('rsi_{}.json'.format(self.stock), 'r') as f:
				self.rsi_data = json.load(f)

			with open('stoch_{}.json'.format(self.stock), 'r') as f:
				self.stoch_data = json.load(f)

			with open('macd_{}.json'.format(self.stock), 'r') as f:
				self.macd_data = json.load(f)

			with open('adr_{}.json'.format(self.stock), 'r') as f:
				self.adr_data = json.load(f)
		elif mode == 'live':
			self.price_data = requests.get(price_str).json()
			self.rsi_data = requests.get(rsi_str).json()
			self.stoch_data = requests.get(stoch_str).json()
			self.macd_data = requests.get(macdext_str).json()
			self.adr_data = requests.get(adr_str).json()

		# Turn into pandas dataframe
		self.price_data = self.price_data['Time Series ({})'.format(self.interval)]
		self.price_data = pd.DataFrame(self.price_data).transpose()
		for col in self.price_data:
			self.price_data[col] = self.price_data[col].astype(float)
		self.rsi_data = pd.DataFrame(self.rsi_data['Technical Analysis: RSI']).transpose()
		for col in self.rsi_data:
			self.rsi_data[col] = self.rsi_data[col].astype(float)
		self.stoch_data = self.stoch_data['Technical Analysis: STOCH']
		self.stoch_data = pd.DataFrame(self.stoch_data).transpose()
		for col in self.stoch_data:
			self.stoch_data[col] = self.stoch_data[col].astype(float)
		self.macd_data = pd.DataFrame(self.macd_data['Technical Analysis: MACDEXT']).transpose()
		for col in self.macd_data:
			self.macd_data[col] = self.macd_data[col].astype(float)
		self.adr_data = pd.DataFrame(self.adr_data['Technical Analysis: ATR']).transpose()
		for col in self.adr_data:
			self.adr_data[col] = self.adr_data[col].astype(float)
'''
