import pandas as pd

from stock_analyzer import  Stockalyzer
import alpaca_trade_api as tradeapi
from screener import Screener

class Trader:
    def __init__(self):
        self.api = tradeapi.REST('AKO60D937GTSFKPNEWEI', 'rstzhpuuGzhBpJ3ojwT4oswGybvBJcOcfGEpGKwr', 'https://api.alpaca.markets')
        self.account = self.api.get_account()
        self.positions = self.api.list_positions()

    def evalPositions(self):
        orders = []
        for pos in self.positions:
            symbol = pos.symbol.strip()
            s = Stockalyzer(symbol, self.api)
            if s.get_analysis() != 'Buy':
                self.api.submit_order(symbol, qty=pos['qty'], side='sell', type='market')
                orders.append(symbol)
        return orders

    def buyPositions(self):
        screener = Screener(self.api)
        buy_list = screener.buy
        buying_power = self.account.buying_power
        best_stock = buy_list.iloc[pd.to_numeric(buy_list['Score']).idxmax()]
        buy_amount = buying_power / best_stock['Price']
        self.api.submit_order(best_stock['Symbol'], qty=buy_amount, side='buy', type='market')
        return best_stock