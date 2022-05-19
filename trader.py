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
            symbol = pos['symbol'].strip()
            s = Stockalyzer(symbol, self.api)
            if s.getAnalysis() != 'Buy':
                self.api.submit_order(symbol, qty=pos['qty'], side='sell', type='market')
                orders.append(symbol)
        return orders

    def buyPositions(self):
        screener = Screener(self.api)
        buy_list = screener.buy
        buying_power = self.account['buying_power']
        # TODO determine best from buy list
        min_stock = buy_list.iloc[0]
        for stock in buy_list:
            if stock['Price'] < min_stock['Price']:
                min_stock = stock
        buy_amount = buying_power / min_stock['Price']
        self.api.submit_order(min_stock['Symbol'], qty=buy_amount, side='buy', type='market')
        return min_stock