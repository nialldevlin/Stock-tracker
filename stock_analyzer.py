import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import deque
import argparse
import pickle

# Credit https://zhenyu0519.github.io/2020/07/08/lc346/

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="modify output verbosity", 
                    action = "store_true")
args = parser.parse_args()


class MovingAverage:

    def __init__(self, size: int):
        """
        Initialize your data structure here.
        """
        self.queue = deque()
        self.size = size

    def next(self, val: int) -> float:
        if len(self.queue) == self.size:
            self.queue.popleft()
            self.queue.append(val)
        else:
            self.queue.append(val)
        return sum(self.queue)/len(self.queue)

class Stockalyzer:
	def __init__(self, stock, ticker, history, short_avg=30, long_avg=150, pdg=2):
		self.stock = stock
		self.short_avg = short_avg
		self.long_avg = long_avg
		self.ticker = ticker
		self.history = history
		self.pdg = pdg

	def getAnalysis(self, last_transaction, last_price):
		"""
		Returns an analysis of given stock in terms of a buy,
		sell, or hold position.
		Return: string 'Buy', 'Sell', or 'Hold'
		"""
		last_s_avg = self.history['Close'].tail(self.short_avg).mean()
		last_l_avg = self.history['Close'].tail(self.long_avg).mean()
		current_price = self.history['Close'][-1]
		last_price = self.history['Close'][-2]
		last_last_price = self.history['Close'][-3]
		ma_derivative = current_price - last_price
		last_ma_derivative = last_price - last_last_price
		if args.verbose:
			print('Current Price: {:.2f}, Current Derivative: {}'.format(current_price, ma_derivative))

		if abs(ma_derivative) <= self.pdg: # flat, turn point, hold till rise/drop
			return 'Hold'
		elif ma_derivative > self.pdg: # rising
			# If last was turn point and haven't bought and rising, buy
			if abs(last_ma_derivative) <= self.pdg and last_transaction != 'Buy': 
				return 'Buy'
			else: # was rising or already bought, hold
				return 'Hold'
		elif ma_derivative < -1 * self.pdg: # falling
			# If last was turn point and havent sold and falling, sell
			if abs(last_ma_derivative) <= self.pdg and last_transaction != 'Sell':
				return 'Sell'
			else: # was rising or already sold, hold
				return 'Hold'

		"""		
		print(hist_d_plt)

		if abs(ma_derivative) <= 1: # if flat, at turn point. Wait till rise/fall to buy/sell
			new_mode = ('t', )
		elif ma_derivative > 1: # Rising
			new_mode = 'r'
		elif ma_derivative < -1: # falling
			new_mode = 'f'

		if new_mode != 't':
			modes.reverse()
			i = 0
			last_not_flat = modes[i]
			while last_not_flat == 't': #In case its  been flat for a while
				i += 1
				last_not_flat = modes[i]
			if last_not_flat == 'f': # was falling last
				if new_mode == 'r': # now rising, buy
					if args.verbose:
						print("Buy {} at {}".format(stock, current_price))
					return 'Buy'
				elif new_mode == 'f': # still falling, hold
					return 'Hold'
			elif last_not_flat == 'r': # was rising last
				if new_mode == 'f': # now falling, sell
					if args.verbose:
						print("Sell {} at {}".format(stock, current_price))
					return 'Sell'
				elif new_mode == 'r': # still rising, hold
					return 'Hold'"""

	def getStockData(self):
		return self.history['Close']

	def getCurrentPrice(self):
		return self.ticker.info['currentPrice']

	def display(self):
		hist = self.getStockData()
		hist.plot(label="{} data".format(self.stock))
		rl_avg_s = hist.rolling(window=self.short_avg).mean()
		print(rl_avg_s)
		rl_avg_s.plot(label="{} rolling average short ({})".format(self.stock, self.short_avg))
		rl_avg_l = hist.rolling(window=self.long_avg).mean()
		rl_avg_l.plot(label="{} rolling average short ({})".format(self.stock, self.long_avg))
		plt.legend(loc="upper left")
		plt.show()

	def runSimulation(self, startingBalance, buyAmount):
		balance = startingBalance
		ba = buyAmount
		num_stock = 0
		data = self.getStockData()
		last_transaction = ''
		last_price = 0
		for index, price in zip(data.index, data):
			data_slice = data[:index]
			if len(data_slice) > 20:
				current_price = data_slice[-1]
				last_price = data_slice[-2]
				ma_derivative = data_slice.diff().tail(self.short_avg).mean()
				last_ma_derivative = data_slice.diff().tail(self.long_avg).mean()
				if args.verbose:
					print('Current Price: {:.2f}, Current Derivative: {}, {}'.format(current_price, ma_derivative, last_ma_derivative))
				printHold = False
				if ma_derivative > self.pdg and last_ma_derivative <= 0:
					if ba * current_price <= balance:
						balance -= ba * current_price
						num_stock += ba
						last_transaction = 'Buy'
						last_price = current_price
						if args.verbose:
							print("Bought {} of {} at {}".format(ba, self.stock, current_price))
					else:
						if args.verbose:
							print("Not Bought {} of {} at {}".format(ba, self.stock, current_price))
				elif ma_derivative < -1 * self.pdg and last_ma_derivative >= 0:
					if num_stock >= ba:
						balance += ba * current_price
						num_stock -= ba
						last_transaction = 'Sell'
						last_price = current_price
						if args.verbose:
							print("Sold {} of {} at {}".format(ba, self.stock, current_price))
					else:
						if args.verbose:
							print("Not Sold {} of {} at {}".format(ba, self.stock, current_price))
		return balance, num_stock


stock = 'MSFT'
msft = yf.Ticker(stock)
hist = msft.history(interval='1d', period='5y')
#for timestamp in pd.date_range(start=(datetime.now() - timedelta(365*5)), end=datetime.now()).to_pydatetime():
stockbot = Stockalyzer(stock, msft, hist, short_avg=10, long_avg=120, pdg=0.1)
stockbot.display()
#balance, num_stock = stockbot.runSimulation(1000, 2)
#print("Starting from $1000, current balance ${}".format(balance + num_stock * stockbot.getCurrentPrice()))
"""
if analysis == 'Buy':
	if buy_amount * data[0] <= current_balance:
		current_balance -= buy_amount * data[0]
		num_stock += buy_amount
		if args.verbose:
			print("Bought {} of {} at {}".format(buy_amount, stock[0], data[0]))
	else:
		if args.verbose:
			print("Not Bought {} of {} at {}".format(buy_amount, stock[0], data[0]))
elif analysis == 'Sell':
	if num_stock >= buy_amount:
		current_balance += buy_amount * data[0]
		num_stock -= buy_amount
		if args.verbose:
			print("Sold {} of {} at {}".format(buy_amount, stock[0], data[0]))
	else:
		if args.verbose:
			print("Not Sold {} of {} at {}".format(buy_amount, stock[0], data[0]))
else:
	if args.verbose:
		print("Hold {} - {}".format(stock[0], data[0]))
net = current_balance + (num_stock * price)
print('Current balance: ${:.2f}'.format(current_balance))
print('Current stock: {}'.format(num_stock))
print('Net amount: {:.2f}'.format(current_balance + num_stock * t.info['currentPrice']))"""
