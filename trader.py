import pandas as pd

from stock_analyzer import  Stockalyzer
from alpaca.trading.client import TradingClient
from screener import Screener
import pandas as pd
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
import warnings

class Trader:
    """
    Trade stocks with Alpaca API

    Uses technical analysis to find stocks to buy. Will implement short selling later.

    ...

    Methods
    -------
    evalPositions()
        Deprecated

    buyPositions(margin=0.9)
        Buys stocks with stop/limit order up to margin percent of buying power
    """
    # TODO implement short sell

    def __init__(self, verbose=True, live=True):
        """Set up API, account, get current positions, get screener data

        :param verbose: Verbose output, bool
        :param live: bool, true for current data - false for testing, uses data from file
        """
        self.v = verbose
        self.api = TradingClient('PKDMSL71FTPAAI5436AH', 'HTm4IdaQsdXjp4LbSQHtrKtZsX7Z62ehvhWL4z3b', paper=True)
        self.account = self.api.get_account()
        self.positions = self.api.get_all_positions()

        if live:
            screener = Screener()
            self.data = screener.getData()
            self.data.to_csv('test_data.csv')
        else:
            self.data = pd.read_csv('test_data.csv')

    def evalPositions(self):
        """Evaluate current positions. Deprecated

        :return: orders submitted
        """
        warnings.warn("This function is deprecated. Now automatically incorporated into BuyPositions", DeprecationWarning)
        orders = []
        for pos in self.positions:
            symbol = pos.symbol
            print(symbol)
            s = Stockalyzer(symbol)
            print(s.price)
            if s._get_analysis() != 'Buy':
                market_order_data = MarketOrderRequest(symbol=symbol,
                                                       qty=pos.qty,
                                                       side=OrderSide.SELL,
                                                       time_in_force=TimeInForce.DAY,
                                                       )
                market_order = self.api.submit_order(market_order_data)
                print(market_order)
        return orders

    def buyPositions(self, margin=0.9):
        """Buys stocks with stop/limit order up to margin percent of buying power

        Buys equal dollar amount of each stock using Alpaca api based on technical indicator analysis

        :param margin: fraction of buying power to use as float from 0 to 1
        :return: Orders submitted
        """
        buy_list = self.data[self.data['Analysis'] == 'Buy']

        # best_stocks = buy_list.loc[buy_list['Score'] == buy_list['Score'].max()]
        best_stocks = buy_list

        if self.v:
            print('Best Stocks:')
            print(best_stocks)

        buying_power = float(self.account.buying_power) * margin
        if self.v:
            print('Buying Power: ', buying_power)

        buy_amount = round(buying_power / len(best_stocks.index), 2)
        if self.v:
            print('Buy Amount: ', buy_amount)

        orders = []
        for index, stock in best_stocks.iterrows():
            if self.v:
                print('Current Stock:')
                print(stock)

            market_order_data = MarketOrderRequest(symbol=stock['Symbol'],
                                                   notional=buy_amount,
                                                   type=OrderType.STOP_LIMIT,
                                                   side=OrderSide.BUY,
                                                   limit_price=stock['Limit'],
                                                   stop_price=stock['Stop'],
                                                   time_in_force=TimeInForce.DAY)
            market_order = self.api.submit_order(market_order_data)
            orders.append(market_order)

            if self.v:
                print(market_order_data)
        return orders

    def shortPositions(self, margin=0.5, t_percent=0.05):
        """Shorts stocks with stop/limit order up to margin percent of buying power

                Loops through each stock list, shorts 1 of each starting with cheapest until no more
                buying power

                :param margin: fraction of buying power to use as float from 0 to 1
                :param t_percent: trailing percent for trailing stop loss
                :return: Orders submitted
                """
        short_list = self.data[self.data['Analysis'] == 'Sell']

        short_list.sort_values('Price')
        short_list.reset_index(drop=True)
        best_stocks = short_list

        if self.v:
            print('Best Stocks:')
            print(best_stocks)

        buying_power = float(self.account.buying_power) * margin
        if self.v:
            print('Buying Power: ', buying_power)

        orders = []
        cont_trade = True
        i = 0
        l = len(best_stocks.index)
        total_shorted_cash_amount = 0
        while cont_trade:
            stock = best_stocks.iloc[i]
            if self.v:
                print('Current Stock:')
                print(i, ': ', stock)
            try:
                market_order_data = MarketOrderRequest(symbol=stock['Symbol'],
                                                       qty=1,
                                                       type=OrderType.TRAILING_STOP,
                                                       side=OrderSide.SELL,
                                                       trail_percent=t_percent,
                                                       time_in_force=TimeInForce.DAY)

                if self.v:
                    print(market_order_data)

                market_order = self.api.submit_order(market_order_data)
                orders.append(market_order)
                total_shorted_cash_amount += stock['Price']
            except Exception as ex:
                cont_trade = False
                print(stock, ex)

            if total_shorted_cash_amount >= buying_power * margin:
                cont_trade = False

            i += 1
            i = i % l
        return orders
