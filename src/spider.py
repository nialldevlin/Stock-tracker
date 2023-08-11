import yfinance as yf
import numpy as np
import pandas as pd
from tqdm import tqdm
import logging


class Spider:
    """
    Gathers S&P stock data from the web
    """

    def __init__(self, period="max", interval="1d", tickers="all", csv="", rw=""):
        self.ticker_web_url = (
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )
        if tickers == "all":
            logging.info("Downloading tickers")
            table = pd.read_html(self.ticker_web_url)
            df = table[0]
            sp500 = df["Symbol"]
            self.symbols = set(sp500.values.flatten())
        else:
            if not isinstance(tickers, list):
                raise ValueError("tickers must be 'all' or a list")
            self.symbols = set(tickers)
        self.tickers = yf.Tickers(' '.join(x for x in self.symbols))
        self.csv = csv
        self.period = period
        self.interval = interval
        self.rw = rw
        if self.csv and self.rw == "r":
            self.data = pd.read_csv(self.csv, index_col=0)
        else:
            logging.info("Downloading stock data")
            self.data = yf.download(self.symbols, period=self.period, interval="1d")['Close']
            self.symbols = self.data.columns
            if self.csv and self.rw == "w":
                self.data.to_csv(self.csv)
        self.data.index = pd.to_datetime(self.data.index)

    def getCurrentPrice(self, ticker):
        return self.tickers.tickers[ticker].fast_info["lastPrice"]

    def getPrice(self, ticker, timestamp):
        return self.data[ticker].loc[timestamp]
