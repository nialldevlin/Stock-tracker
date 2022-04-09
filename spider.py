#!../stracker/bin/python3

from stocksymbol import StockSymbol
from powerx import PowerX

class Spider:
	def __init__(self, market='america'):
		with open('stocksymbol_apikey.txt', 'rb') as f:
			self.apikey = f.read()

		ss = StockSymbol(self.api_key)
		self.stock_list = ss.get_symbol_list(market=market)
		self.top_stocks = self.crawl()

	def crawl(self):
		for stock in self.stock_list:
			