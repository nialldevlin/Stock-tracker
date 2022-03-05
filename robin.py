#!/home/pi/Documents/Stock-tracker/stocktracker/bin/python3

import robin_stocks as r

class StockBuyer:
    def __init__(self):
        login = r.login('NiallD1628','ncd118*AB')
        my_stocks = robin_stocks.build_holdings()

    def displayHoldings(self, my_stocks):
        for key, value in my_stocks.items():
            print(key, value)

    def buyStock(self, stock, shares):
        r.order_buy_market(stock, shares);

    def sellStcok(self, stock, shares):
        r.order_sell_market(stock, shares):

