#!../stracker/bin/python3

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
from powerx import PowerX
import pandas as pd

class PowerX:
	def __init__(self, ticker, exchange):
		self.ticker = ticker

		handler = TA_Handler(
		    symbol=self.ticker,
		    exchange=exchange,
		    screener="america",
		    interval=Interval.INTERVAL_1_DAY
		)

		analysis = handler.get_analysis()

		self.oscillators = analysis.oscillators
		self.indicators = analysis.indicators
		self.summary = analysis.summary

		self.rsi = indicators['RSI']
		self.stochk = indicators['Stoch.K']
		self.stochd = indicators['Stoch.D']
		self.macd = indicators['MACD.macd']
		self.sig = indicators['MACD.signal']

		if rsi > 50 and stochk > 50 and stochd > 50 and macd > sig:
			self.powerXAnalysis = 'Buy'
		elif rsi < 50 and stochk < 50 and stochd < 50 and macd < sig:
			self.powerXAnalysis = 'Sell'
		else:
			self.powerXAnalysis = 'Hold'

	def __bool__(self):
		# Large Market Cap > 100B
		# Current price > SMA 50 > SMA 100 > SMA 200
		# PowerX profitable
		sma50 = self.indicators['SMA50']
		sma100 = self.indicators['SMA100']
		sma200 = self.indicators['SMA200']
		uptrend = sma50 > sma100 and sma100 > sma200
		buy = self.powerXAnalysis == 'Buy' and self.summary['RECOMMENDATION'] == 'Buy'
		return buy and uptrend

class Spider:
	def __init__(self, market='america'):
		self.top_stocks = self.crawl()

	def crawl(self):
		nasdaq = pd.read_csv('nasdaq.csv')
		nyse = pd.read_csv('nyse.csv')
		good_stocks = pd.DataFrame()
		for stock in nasdaq:
			powx = PowerX(stock['Symbol'], 'nasdaq')
			if powx:
				good_stocks.append(stock)
		return good_stocks
