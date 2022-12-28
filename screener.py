import yahoo_fin.stock_info as yfinfo
import pandas as pd
from stock_analyzer import Stockalyzer
from tqdm import tqdm
import warnings

class Screener:
    """
    Stock screener

    Compiles list of S&P 500 stocks, performs analysis on each based on technical indicators to determine buy/sell/hold

    ...

    Methods
    -------
    getMarketAvgAnalysis()
        Performs analysis on S&P 500. Under Construction

    getData()
        Gets list of S&P 500, analyses each stock in list, returns dataframe. Must run first

    getBuy()
        Returns list of stocks with analysis 'Buy'. Must run after getData()

    getSell()
        Returns list of stocks with analysis 'Sell'. Must run after getData()
    """
    def __init__(self, verbose=True):
        self.verbose = verbose
        if self.verbose:
            print('Getting stock list')
        self.list = yfinfo.tickers_sp500()
        self.data = pd.DataFrame()

    def getMarketAvgAnalysis(self):
        """Get Analysis of S&P 500 to determine bear or bull market. Under construction

        :return: Buy, Sell, or Hold
        """
        # TODO this needs work
        s_and_p = Stockalyzer('^GSPC')
        return s_and_p.analysis

    def getData(self):
        """Get analysis for stocks in S&P 500

        :return: pandas dataframe, columns: 'Symbol', 'Analysis', 'Price', 'Stop', 'Limit', 'Score'
        """

        if self.verbose:
            print('Evaluating stock list')

        list = self.list
        s_list = []

        for ticker in tqdm(list):
            # TODO: get data for all tickers at once
            try:
                sto = Stockalyzer(ticker)
                s_list.append(sto.toSeries())
            except Exception as ex:
                print(ticker, ex)

        df = pd.concat(s_list, axis=1).T
        self.data = df
        return df

    def getBuy(self):
        """Get stocks with analysis 'Buy' from data compiled

        :return: pandas dataframe, columns: 'Symbol', 'Analysis', 'Price', 'Stop', 'Limit', 'Score'
        """

        if self.data.empty:
            raise Exception('getData must be run first')
        data = self.data
        df = data.loc[data['Analysis'] == 'Buy']
        return df

    def getSell(self):
        """Get stocks with analysis 'Sell' from data compiled

        :return: pandas dataframe, columns: 'Symbol', 'Analysis', 'Price', 'Stop', 'Limit', 'Score'
        """

        if self.data.empty:
            raise Exception('getData must be run first')
        data = self.data
        df = data.loc[data['Analysis'] == 'Sell']
        return df