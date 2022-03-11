#!/home/pi/Documents/Stock-tracker/stocktracker/bin/python3

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class Stockalyzer:
	def __init__(self, stock, ticker, history, short_avg=200, long_avg=1000, pgd=6, sda=2):
		"""
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: stock - 4 letter stock name eg. 'MSFT'
				ticker - yfinance stock ticker
				history - pandas dataframe with history of stock
				short_avg - number in hours for short term average
				long_avg - number in hours for long term average
				pgd - profitable gain difference. Amount (in $) difference between averages considered signifigant
				sda - signal dollar amount. Once difference is past pgd + sda, hold while rise/fall
		"""
		self.stock = stock
		self.analysis = ''
		self.short_avg = short_avg
		self.long_avg = long_avg
		self.ticker = ticker
		self.history = history
		self.pgd = pgd
		self.sda = sda

	def getAnalysis(self):
		"""
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		"""
		data = self.getStockData()
		return self.LongPriceAvgAnalysis(data)

	def LongShortAvgAnalysis(self, dataset):
		"""
		If short term average is above long term average by
		pgd, stock is rising. Send buy signal until difference
		is above pgd + sda. If short term average is below long term
		average by same criteria, send sell signal While stock
		is rising/falling and buy/sell signal is over, send
		hold signal.
		Params: dataset to analyze
		Return: string 'Buy', 'Sell', or 'Hold'
		"""
		short_avg = dataset[-1 * self.short_avg:].mean()
		long_avg = dataset[-1 * self.long_avg:].mean()
		if short_avg - long_avg > self.pgd and short_avg - long_avg < self.pgd + self.sda:
			self.analysis = 'Buy'
			return 'Buy'
		elif long_avg - short_avg > self.pgd and long_avg - short_avg < self.pgd + self.sda:
			self.analysis = 'Sell'
			return 'Sell'
		else:
			self.analysis = 'Hold'
			return 'Hold'
		

	def LongPriceAvgAnalysis(self, dataset):
		"""
		Current stock price is compared to short term std
		of dataset.
		Params: dataset to analyze
		Return: string 'Buy', 'Sell', or 'Hold'
		"""
		short_avg = dataset[-1 * self.short_avg:].std()
		current_price = self.getCurrentPrice()
		if short_avg >= current_price and short_avg <= current_price + self.sda:
			self.analysis = 'Buy'
			return 'Buy'
		elif short_avg < current_price and short_avg >= current_price - self.sda:
			self.analysis = 'Sell'
			return 'Sell'
		else:
			self.analysis = 'Hold'
			return 'Hold'

	def getStockData(self):
		"""
		Return stock close for each period in history
		"""
		return self.history['Close']

	def getCurrentPrice(self):
		"""
		Returns current price of stock
		"""
		return self.history['Close'][-1]

	def display(self):
		"""
		Displays graph of stock and averages with matplotlib
		"""
		hist = self.getStockData()
		hist.plot(label="{} data".format(self.stock))
		if self.analysis == 'Buy':
			color = 'chartreuse'
		elif self.analysis == 'Sell':
			color = 'r'
		elif self.analysis == 'Hold':
			color = 'dimgray'
		rl_avg_s = hist.rolling(window=self.short_avg).mean()
		rl_avg_s.plot(color=color, label="{} rolling average short ({:.2f})".format(self.stock, self.short_avg))
		rl_avg_l = hist.rolling(window=self.long_avg).mean()
		rl_avg_l.plot(color='orchid', label="{} rolling average long ({:.2f})".format(self.stock, self.long_avg))
		plt.xlabel("Date")
		plt.ylabel("Price")
		plt.title("{} Stock Data: {} at {:.2f}".format(self.stock, self.analysis, self.getCurrentPrice()))
		plt.legend(loc='upper left')
		plt.show()
		plt.clf()

	def saveAsPng(self, filename=''):
		"""
		Saves graph as png to filename
		If none specified, defaults to {stock}.png
		"""
		if filename == '':
			filename = '{}.png'.format(self.stock)
		hist = self.getStockData()
		hist.plot(label="{} data".format(self.stock))
		if self.analysis == 'Buy':
			color = 'chartreuse'
		elif self.analysis == 'Sell':
			color = 'r'
		elif self.analysis == 'Hold':
			color = 'dimgray'
		rl_avg_s = hist.rolling(window=self.short_avg).mean()
		rl_avg_s.plot(color=color, label="{} rolling average short ({:.2f})".format(self.stock, self.short_avg))
		rl_avg_l = hist.rolling(window=self.long_avg).mean()
		rl_avg_l.plot(color='orchid', label="{} rolling average long ({:.2f})".format(self.stock, self.long_avg))
		plt.xlabel("Date")
		plt.ylabel("Price")
		plt.title("{} Stock Data: {} at {:.2f}".format(self.stock, self.analysis, self.getCurrentPrice()))
		plt.legend(loc='upper left')
		plt.savefig(filename)
		plt.clf()

	def runSimulation(self, startingBalance, buyAmount, startingStock=0, verbose=False):
		"""
		Runs simulation on stock history. Analysis is run on stock data to a certain date
		Starts with given balance and starting stock (default 0) and invests based on
		analysis.
		Params: startingbalance - amount to start with in $
				buyAmount - amount of stock to buy each time
				startingStock - amount of stock to start with
		Return: ending balance, number of stock
		"""
		balance = startingBalance
		ba = buyAmount
		num_stock = startingStock
		data = self.getStockData().values
		last_transaction = ''
		last_price = 0
		for i in range(self.short_avg, data.size):
			data_slice = data[:i]
			if len(data_slice) > self.short_avg:
				current_price = data_slice[-1]
				analysis = runAnalysis(data_slice)
				if analysis == 'Buy':
					if ba * current_price <= balance:
						balance -= ba * current_price
						num_stock += ba
						if verbose:
							print("Bought {} of {} at {}".format(ba, self.stock, current_price))
					else:
						if verbose:
							print("Not Bought {} of {} at {}".format(ba, self.stock, current_price))
				elif analysis == 'Sell':
					if num_stock >= ba:
						balance += ba * current_price
						num_stock -= ba
						if verbose:
							print("Sold {} of {} at {}".format(ba, self.stock, current_price))
					else:
						if verbose:
							print("Not Sold {} of {} at {}".format(ba, self.stock, current_price))
				else:
					if printHold:
						print("Hold {} at {}".format(self.stock, current_price))
		return balance, num_stock
