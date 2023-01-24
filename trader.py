import pandas as pd

from stock_analyzer import  Stockalyzer
from alpaca.trading.client import TradingClient
from screener import Screener
import pandas as pd
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderClass
import warnings
from enum import Enum

class Side(Enum):
    BUY = 0
    SELL = 1

class Trader:
    """
    Trade stocks with Alpaca API

    Uses technical analysis to find stocks to buy. Will implement short selling later.

    ...

    Methods
    -------
    evalPositions()
        Deprecated

    tradePositions(margin=0.9)
        Buys/sells stocks with stop/limit order up to margin percent of buying power
    """

    def __init__(self, verbose=True, live=True):
        """Set up API, account, get current positions, get screener data

        :param verbose: Verbose output, bool
        :param live: bool, true for current data - false for testing, uses data from file
        """
        self.v = verbose
        self.api = TradingClient('PKYKGKUGPVDK7OGSIRSD', 'vvh1Hvgc0MaNIi0S7fw2dtjF7qOogoiI0kNt6HoY', paper=True)
        self.account = self.api.get_account()
        self.positions = self.api.get_all_positions()

        if live:
            self.screener = Screener()
            self.data = self.screener.getData()
            self.data.to_csv('test_data.csv')
            self.buy = self.screener.getBuy()
            self.sell = self.screener.getSell()
        else:
            self.data = pd.read_csv('test_data.csv')
            self.buy = self.data.loc[self.data['Analysis'] == 'Buy']
            self.sell = self.data.loc[self.data['Analysis'] == 'Sell']

    def getBuySellReccomendation(self):
        if self.screener.getMarketAvgAnalysis() == 'Buy':
            return Side.BUY
        else:
            return Side.SELL

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

    def tradePositions(self, margin=0.9, side=Side.BUY):
        """Buys/Shorts stocks with stop/limit order up to margin percent of buying power

        Loops through each stock list, trades 1 of each starting with cheapest until no more
        buying power. Submits take profit and stop orders.

        :param margin: fraction of buying power to use as float from 0 to 1
        :return: Orders submitted
        """
        if side == Side.BUY:
            buy_list = self.buy
        elif side == Side.SELL:
            buy_list = self.sell
        else:
            raise ValueError('side must be Side.BUY or Side.SELL')

        # best_stocks = buy_list.loc[buy_list['Score'] == buy_list['Score'].max()]
        best_stocks = buy_list

        if self.v:
            print('Best Stocks:')
            print(best_stocks)

        buying_power = float(self.account.buying_power) * margin
        if self.v:
            print('Buying Power: ', buying_power)

        total = best_stocks['Price'].sum()
        amt = int(buying_power/total)

        orders = []
        total_bought_cash_amount = 0

        for index, stock in best_stocks.iterrows():
            if self.v:
                print(f'Current Stock:{stock}')

            try:
                if side == Side.BUY:
                    stop = round(stock['Price'] - stock['ADR'], 2)
                    limit = round(stock['Price'] + stock['ADR'] * 2, 2)
                    o_side = OrderSide.BUY
                else:
                    stop = round(stock['Price'] + stock['ADR'], 2)
                    limit = round(stock['Price'] - stock['ADR'] * 2, 2)
                    o_side = OrderSide.SELL

                market_order_data = MarketOrderRequest(symbol=stock['Symbol'],
                                                       qty=amt,
                                                       type=OrderType.MARKET,
                                                       side=o_side,
                                                       order_class=OrderClass.BRACKET,
                                                       take_profit={'limit_price': limit},
                                                       stop_loss={'stop_price': stop},
                                                       time_in_force=TimeInForce.GTC)

                if self.v:
                    print(market_order_data)

                market_order = self.api.submit_order(market_order_data)
                orders.append(market_order)
                total_bought_cash_amount += (stock['Price'] * amt)

                if self.v:
                    print(market_order_data)

            except Exception as ex:
                warnings.warn(f"{stock}:{ex}")

            if self.v:
                print(f'Total bought: ${total_bought_cash_amount}')

        return orders
