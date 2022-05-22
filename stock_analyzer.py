import numpy as np
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import yahoo_fin.stock_info as yf
from dotenv import load_dotenv
import os

class Stockalyzer:
	def __init__(self, symbol, interval=tradeapi.TimeFrame.Hour, mode='store'):
		'''
		Class to analyze stocks. Also contains simulator to check algorithm
		Params: ticker - 4 letter stock name eg. 'MSFT'
				interval='daily'
		'''
		load_dotenv()

		if interval == tradeapi.TimeFrame.Day:
			self.tpm = 1
		elif interval == tradeapi.TimeFrame.Hour:
			self.tpm = 16

		self.params = {
			'RSI': {
				'interval': interval,
				'time_period': 7 * self.tpm,
				'series_type': 'close'
			},
			'STOCH': {
				'interval': interval,
				'fastkperiod': 14 * self.tpm,
				'slowkperiod': 3 * self.tpm,
				'slowdperiod': 3 * self.tpm
			},
			'MACDEXT': {
				'interval': interval,
				'series_type': 'close',
				'fastperiod': 12 * self.tpm,
				'slowperiod': 26 * self.tpm,
				'signalperiod': 9 * self.tpm,
				'fastmatype': 1,
				'slowmatype': 1,
				'signalmatype': 1
			},
			'ATR': {
				'interval': interval,
				'time_period': 7 * self.tpm
			}
		}

		self.stock = symbol
		live_trading = 'https://api.alpaca.markets'
		paper_trading = 'https://paper-api.alpaca.markets'
		# Be sure to change keys in .env file as well
		self.api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), live_trading)
		self.account = self.api.get_account()
		self.interval = interval
		self.analysis = ''

		start = datetime.today().strftime('%Y-%m-%d')
		end = (datetime.today() - timedelta(365)).strftime('%Y-%m-%d')
		self.price_data = self.getPriceData(end, start, interval)
		if self.price_data.empty:
			raise AttributeError('No Price Data found for {}'.format(self.stock))
		self.rsi_data = self.getRSIData()
		self.stochk_data, self.stochd_data = self.getStochData()
		self.macd_data, self.macd_sig_data = self.getMACDData()
		self.avg_50_data = self.price_data['close'].rolling(50).mean()
		self.avg_200_data = self.price_data['close'].rolling(200).mean()

		self.rsi = self.getRSI()
		self.stochk, self.stochd = self.getStoch()
		self.macd, self.macd_sig = self.getMACD()
		self.adr = self.getADR()
		self.price = self.getPrice()
		self.stop = self.price - self.adr
		self.sell = self.price + self.adr * 2
		self.avg_50 = self.avg_50_data.tail(1)[0]
		self.avg_200 = self.avg_200_data.tail(1)[0]

		self.balance_sheet = yf.get_balance_sheet(self.stock)
		self.income_statement = yf.get_income_statement(self.stock)
		self.cfs = yf.get_cash_flow(self.stock)
		self.years = self.balance_sheet.columns

	def getPriceData(self, start, end, interval):
		return self.api.get_bars(self.stock, interval, start, end, adjustment='raw').df

	def getRSIData(self):
		# Relative Strength Indicator
		rsi_period = 7
		change = self.price_data['close'].tail(rsi_period * 3).diff()
		up = change.clip(lower=0)
		down = -1 * change.clip(upper=0)
		avgu = up.ewm(span=rsi_period, adjust=False).mean()
		avgd = down.ewm(span=rsi_period, adjust=False).mean()
		rs = avgu / avgd
		rsi = 100 - (100 / (1 + rs))
		return rsi

	def getStochData(self):
		# Stochastic oscillator
		data = self.price_data.tail(30)
		low_d = data['low'].transform(lambda x: x.rolling(window=3).min())
		high_d = data['high'].transform(lambda x: x.rolling(window=3).max())
		low_k = data['low'].transform(lambda x: x.rolling(window=14).min())
		high_k = data['high'].transform(lambda x: x.rolling(window=14).max())

		stochd = ((data['close'] - low_d) / (high_d - low_d)) * 100
		stochk = ((data['close'] - low_k) / (high_k - low_k)) * 100
		stochd = stochd.rolling(window = 3).mean()
		stochk = stochk.rolling(window = 14).mean()
		return stochk, stochd

	def getMACDData(self):
		# Moving Average Convergence Divergence
		data = self.price_data.tail(30)
		sema = data['close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
		lema = data['close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
		macd = sema - lema
		sig = macd.transform(lambda x: x.ewm(span=9, adjust=False).mean())
		return macd, sig

	def getADR(self):
		# Average Daily Range
		l = 7 * self.tpm
		last_week = self.price_data.tail(l)
		daily_ranges = np.array([])
		for i in range(0, l, self.tpm):
			day = last_week.iloc[i:i+self.tpm]
			daily_high = day['high'].max() 
			daily_low = day['low'].min()
			daily_ranges = np.append(daily_ranges, daily_high - daily_low)

		adr = np.mean(daily_ranges)
		return adr

	def getPrice(self):
		return self.price_data['close'].iloc[-1]- self.adr/4

	def getRSI(self):
		return self.rsi_data[-1]

	def getStoch(self):
		return self.stochk_data[-1], self.stochd_data[-1]

	def getMACD(self):
		return self.macd_data[-1], self.macd_sig_data[-1]

	def getStopPrice(self):
		return self.getPrice() - self.adr

	def getSellPrice(self):
		return self.getPrice() + self.adr * 2

	def profitability(self):
		"""
		Determine profitability of a company using income statement, balance sheet, and cash flow
		:return: p_score - total profitability score from 0 to 4
		"""
		p_score = 0

		# Net Income
		net_income = self.income_statement[self.years[0]]['netIncome']
		net_income_last = self.income_statement[self.years[1]]['netIncome']
		ni_ratio_score = 1 if net_income > net_income_last and net_income > 0 else 0
		p_score += ni_ratio_score

		# Operating Cash Flow
		op_cf = self.cfs[self.years[0]]['totalCashFromOperatingActivities']
		of_cf_score = 1 if op_cf > 0 else 0
		p_score += of_cf_score

		# Return on Assets
		avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]]['totalAssets']) / 2
		avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]]['totalAssets']) / 2
		RoA = net_income / avg_assets
		RoA_last = net_income_last / avg_assets_last
		RoA_score = 1 if RoA > RoA_last else 0
		p_score += RoA_score

		# Accruals
		total_assets = self.balance_sheet[self.years[0]]['totalAssets']
		accruals = op_cf / total_assets - RoA
		acc_score = 1 if accruals > 0 else 0
		p_score += acc_score

		return p_score

	def leverage(self):
		"""
		Determine leverage of a company with balance sheet
		:return: l_score - total leverage score from 0 to 2
		"""
		l_score = 0

		# Long-term debt ratio
		try:
			ltd = self.balance_sheet[self.years[0]]['longTermDebt']
			total_assets = self.balance_sheet[self.years[0]]['totalAssets']
			debt_ratio = ltd / total_assets
			dr_score = 1 if debt_ratio < 0.4 else 0
			l_score += dr_score
		except:
			l_score += 1

		# Current ratio
		current_assets = self.balance_sheet[self.years[0]]['totalCurrentAssets']
		current_liab = self.balance_sheet[self.years[0]]['totalCurrentLiabilities']
		current_ratio = current_assets / current_liab
		cr_score = 1 if current_ratio > 1 else 0
		l_score += cr_score

		return l_score

	def operating_efficiency(self):
		"""
		Determine operating efficency of a company
		:return: oe_score - score representing operating efficency from 0 to 2
		"""
		oe_score = 0

		# Gross margin
		gp = self.income_statement[self.years[0]]['grossProfit']
		gp_last = self.income_statement[self.years[1]]['grossProfit']
		revenue = self.income_statement[self.years[0]]['totalRevenue']
		revenue_last = self.income_statement[self.years[1]]['totalRevenue']
		gm = gp / revenue
		gm_last = gp_last / revenue_last
		gm_score = 1 if gm > gm_last else 0
		oe_score += gm_score

		# Asset turnover
		avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]]['totalAssets']) / 2
		avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]]['totalAssets']) / 2
		at = revenue / avg_assets
		at_last = revenue_last / avg_assets_last
		at_score = 1 if at > at_last else 0
		oe_score += at_score

		return oe_score

	def get_score(self):
		"""
		Returns total score based on profitability, leverage, and operating efficiency
		:return: s - total score from 0 (worst) to 8 (best)
		"""
		s = self.profitability() + self.leverage() + self.operating_efficiency()
		return s

	def get_analysis(self, timestamp='now'):
		'''
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position. Estimated 9% gain
		Return: string 'Buy', 'Sell', or 'Hold'
		'''
		if timestamp == 'now':
			rsi = self.rsi
			stoch = self.stochk
			macd = self.macd > self.macd_sig
			up = self.price > self.avg_50 and self.avg_50 > self.avg_200
		else:
			rsi = self.rsi_data.loc[timestamp]
			stoch = self.stochk_data.loc[timestamp]
			macd = self.macd_data.loc[timestamp] > self.macd_sig_data.loc[timestamp]
			if timestamp in self.avg_200_data.index:
				up = (self.price_data.loc[timestamp] > self.avg_50_data.loc[timestamp]
					  and self.avg_50_data.loc[timestamp] > self.avg_200_data.loc[timestamp])
			else:
				up = True

		if (rsi > 50 and
			stoch > 50 and
			macd and
			up and
			self.get_score() >= 7):
			return 'Buy'
		elif (rsi < 50 and
			  stoch < 50 and
			  macd and
			  not up):
			return 'Sell'
		else:
			return 'Hold'
