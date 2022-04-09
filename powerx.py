#!../stracker/bin/python3

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta
import yfinance as yf

class PowerX:
	def __init__(self, ticker):
		self.ticker = ticker

		handler = TA_Handler(
		    symbol=self.ticker,
		    exchange="NYSE",
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

	def getPowerXAnalysis(self):
		return self.powerXAnalysis

	def getAnalysis(self):
		return self.summary['RECOMMENDATION']

	def getData(self):
		tick = yf.Ticker(self.ticker)
		vol = tick.info['volume']
		regVol = tick.info['regularMarketVolume']
		mcap = tick.info['marketCap']
		price = tick.info['currentPrice']
		return {'volume':vol, 'regularVolume':regVol, 'marketCap':mcap, 'price':price}