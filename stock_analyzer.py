import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json

class Stockalyzer:
	def __init__(self, ticker, interval='daily'):
		'''
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: ticker - 4 letter stock name eg. 'MSFT'
				interval='daily'
		'''
		if interval not in ('daily', '60min'):
			raise ValueError('interval must be daily or 60min')

		self.stock = ticker
		self.price_data = {}
		self.rsi_data = {}
		self.stoch_data = {}
		self.macd_data = {}
		self.adr_data = {}
		self.interval = interval

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

		self.getTechnicalIndicators()
		self.analysis = self.tiaanalysis()
		#self.getAnalysis()

	# TODO: Make this better it sucks
	def getAnalysis(self):
		'''
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		'''
		print(self.rsi_data)
		analysis_data = pd.DataFrame(index=self.stoch_data.index, columns=['price', 'analysis'])
		for i in self.stoch_data.index:
			a = self.tiaanalysis(date=i)
			analysis_data['analysis'][i] = a['analysis']
			analysis_data['price'][i] = a['current_price']
		print(analysis_data)

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

	def tiaanalysis(self, date='now'):
		'''
		Current stock price is compared to short term std
		of dataset.
		Params: dataset to analyze
		Return: dictionary of
			analysis - 'Rise', 'Fall', or 'Hold'
			current price - price of stock
			stop price - price to sell at to cut losses
			sell price - target price to sell at
		'''

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

	def getPriceData(self):
		'''
		Return stock price for each period in history
		'''
		return self.price_data['4. close']

	def getRSIData(self):
		'''
		Return RSI data for each period in history
		'''
		return self.rsi_data

	def getStochasticData(self):
		'''
		Return stochastic data for each period in history
		'''

		return self.stoch_data

	def getMACDData(self):
		'''
		Return MACD data for each period in history
		'''
		return self.macd_data

	def getADRData(self):
		'''
		Return average daily range data for each period in history
		'''
		return self.adr_data

	def getCurrentPrice(self):
		'''
		Returns current price of stock
		'''
		return self.getPriceData().iloc[0]

	#TODO: Display all data
	def display(self):
		'''
		Displays graph of stock and averages with matplotlib
		'''
		hist = self.getPriceData()[::-1]
		if self.analysis['analysis'] == 'Rise':
			color = 'chartreuse'
		elif self.analysis['analysis'] == 'Fall':
			color = 'r'
		else:
			color = 'dimgray'
		hist.plot(color=color, label='{} data'.format(self.stock))
		plt.axhline(y=self.analysis['stop price'], color='r', label='Stop Price')
		plt.axhline(y=self.analysis['sell price'], color='chartreuse', label='Target Price')
		plt.xlabel('Date')
		plt.ylabel('Price')
		plt.xticks(rotation=80)
		plt.title('{} Stock Data: {} at {:.2f}'.format(self.stock, self.analysis['analysis'], self.getCurrentPrice()))
		plt.legend(loc='upper left')
		plt.show()
		plt.clf()

	#TODO: FIX this too
	def saveAsPng(self, filename=''):
		'''
		Saves graph as png to filename
		If none specified, defaults to {stock}.png
		'''
		if filename == '':
			filename = '{}.png'.format(self.stock)
		hist = self.getPriceData()[::-1]
		if self.analysis['analysis'] == 'Rise':
			color = 'chartreuse'
		elif self.analysis['analysis'] == 'Fall':
			color = 'r'
		else:
			color = 'dimgray'
		hist.plot(color=color, label='{} data'.format(self.stock))
		plt.axhline(y=self.analysis['stop price'], color='r', label='Stop Price')
		plt.axhline(y=self.analysis['sell price'], color='chartreuse', label='Target Price')
		plt.xlabel('Date')
		plt.ylabel('Price')
		plt.title('{} Stock Data: {} at {:.2f}'.format(self.stock, self.analysis['analysis'], self.getCurrentPrice()))
		plt.legend(loc='upper left')
		plt.savefig(filename, pad_inches = 1)
		plt.clf()

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

				'''
				If changes to buy:
					buy if able
					log stop/sell price
				if changes to sell or hits stop/sell price:
					sell if able

				'''

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
		return balance, num_stock'''
