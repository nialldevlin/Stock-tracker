from spider import Spider
import pandas as pd


class Simulate(Spider):
    """
    Class Simulate
    Simulate a trading environment. Starts with cash and no stocks,
    and a timestamp at the start of available data. Iterates over
    timestamps, and allows buy, sell, and hold of stocks.

    Class variables
    cash - starting cash
    holdings - dictionary, key is symbol, value is amount
    """

    def __init__(self,
                 starting_cash=100000,
                 start_timestamp="",
                 stop_timestamp="",
                 period="10y",
                 interval="1d",
                 tickers="all",
                 csv="",
                 rw="w"):
        super().__init__(period,
                         interval,
                         tickers,
                         csv,
                         rw)
        self.cash = starting_cash
        if start_timestamp:
            self.timestamp = start_timestamp
            self.stop = stop_timestamp
        else:
            self.timestamp = self.data.index[0]
            self.stop = self.data.index[-1]
        self.holdings = dict.fromkeys(self.symbols, 0)

    def __str__(self):
        return (f"Cash: {self.cash}, "
                f"Timestamp: {self.timestamp.date()}\n"
                f"Total Value: {self.getTotalValue()}, "
                f"Holding: {self.getHoldings()}")

    def _price(self, ticker):
        price = self.data[ticker.upper()].loc[self.timestamp]
        return price if price == price else 0

    def done(self):
        return self.timestamp == self.stop

    def getHoldingsValue(self):
        sum = 0
        for stock, shares in self.getHoldings().items():
            sum += shares * self._price(stock)
        return sum

    def getHoldings(self):
        return {key: value for key, value in self.holdings.items()
                if value != 0}

    def getTotalValue(self):
        return self.cash + self.getHoldingsValue()

    def step(self, actions={}):
        """
        Execute a trading step based on the provided actions.

        This function performs a trading step using the provided actions
        dictionary, where each key represents a stock and the corresponding
        value indicates the amount to be traded.

        :param actions: Dictionary of trading actions.
                        Key: Stock name (string).
                        Value: Amount to be traded (int).
        :type actions: dict
        """
        for s, amt in actions.items():
            stock = s.upper()
            price = self._price(stock)
            if stock not in self.symbols:
                print(f"{stock} is not in available dataset")
                continue
            if price == 0 or price != price:
                print((f"{stock} data for timestep {self.timestamp.date()}"
                        " is not in available dataset"))
                continue
            if amt == 0:
                amt = -self.holdings[stock]
            cost = amt * self._price(stock)
            if cost < self.cash:
                self.cash -= cost;
            else:
                print(f"Not enough cash. Cash left: {self.cash}")
            self.holdings[stock] += amt
        if self.done():
            return
        n = self.data.index.get_loc(self.timestamp)
        self.timestamp = self.data.index[n + 1]
            
