import yfinance as yf
import numpy as np
import pandas as pd
from tqdm import tqdm
import logging

class Spider:
    """
    Gathers S&P stock data from the web
    """
    def __init__(self, period='max', tickers='all', csv='', rw=''):
        self.ticker_web_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        if tickers == 'all':
            self.tickers = self._get_tickers()
        else:
            if not isinstance(tickers, list):
                raise ValueError('tickers must be \'all\' or a list')
            self.tickers = tickers
        self.data = self._get_data(period, csv, rw)
    
    def _get_tickers(self):
        """
        Aquires list of S&P500 tickers
        """
        logging.info('Downloading tickers')
        table=pd.read_html(self.ticker_web_url)
        df = table[0]
        sp500 = df['Symbol']
        return sp500.values.flatten().tolist()
    
    def _get_data(self, period, csv, rw):
        """
        Get stock data from yfinance or csv file
        """
        if csv and rw=='r':
            return pd.read_csv(csv, index_col=0)

        logging.info('Downloading stock data')
        data = yf.download(self.tickers,
                period=period,
                interval='1d')
        data = data['Open']
        self.tickers = data.columns
        
        if csv and rw=='w':
            data.to_csv(csv)

        return data

    def getCurrentPrice(self, symbol):
        ticker = yf.Ticker(symbol)
        return ticker.fast_info['lastPrice']
