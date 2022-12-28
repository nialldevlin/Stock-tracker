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

    def __init__(self, verbose=True):
        """Set up API, account, and get positions

        :param verbose: Verbose output, bool
        """
        self.v = verbose
        self.api = TradingClient('PKDMSL71FTPAAI5436AH', 'HTm4IdaQsdXjp4LbSQHtrKtZsX7Z62ehvhWL4z3b', paper=True)
        self.account = self.api.get_account()
        self.positions = self.api.get_all_positions()

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
        # Live
        # screener = Screener()
        # data = screener.getData()
        # data.to_csv('test_data.csv')
        # buy_list = screener.getBuy()

        # From File: For Testing - Faster
        list = pd.read_csv('test_data.csv')
        buy_list = list[list['Analysis'] == 'Buy']

        #best_stocks = buy_list.loc[buy_list['Score'] == buy_list['Score'].max()]
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