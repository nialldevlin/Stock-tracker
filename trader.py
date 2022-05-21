import pandas as pd
from stock_analyzer import  Stockalyzer
import alpaca_trade_api as tradeapi
from screener import Screener
import sqlite3

class Trader:
	def __init__(self):
		self.api = tradeapi.REST('AKO60D937GTSFKPNEWEI', 'rstzhpuuGzhBpJ3ojwT4oswGybvBJcOcfGEpGKwr', 'https://api.alpaca.markets')
		self.account = self.api.get_account()
		self.positions = self.api.list_positions()

	def evalPositions(self):
		orders = []
		for pos in self.positions:
			symbol = pos.symbol.strip()
			s = Stockalyzer(symbol)
			if s.get_analysis() != 'Buy':
				self.api.submit_order(symbol, qty=pos['qty'], side='sell', type='market')
				orders.append(symbol)
		return orders
	
	def buyPositions(self):
		db = r"/home/proffessordevnito/Documents/Python_Projects/Stock-tracker/stockdb.sqlite"
		conn = sqlite3.connect(db)
		c = conn.cursor()
		sql_query = pd.read_sql_query("SELECT * FROM products", conn)
		cols = [description[0] for description in c.description]
		df = pd.DataFrame(sql_query, columns=cols)
		buy_list = df.loc[df['Analysis'] == 'Buy']
		buying_power = int(self.account.buying_power)
		best_stock = buy_list.iloc[pd.to_numeric(buy_list['Score']).idxmax()]
		
		buy_amount = int(buying_power / best_stock['Price'])
		self.api.submit_order(best_stock['Symbol'], qty=buy_amount, side='buy', type='market')
		return best_stock

