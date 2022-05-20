import yahoo_fin.stock_info as yf
import pandas as pd
from stock_analyzer import Stockalyzer

class Screener:
    def __init__(self, api):
        self.api = api
        print('Getting stock list')
        self.list = yf.tickers_sp500()
        self.data = self.getData()
        self.buy = self.getBuy()

    def getData(self):
        print('Evaluating stock list')
        list = self.list
        indx = ['Symbol', 'Analysis', 'Price', 'Stop', 'Sell', 'Score']
        s_list = []
        i = 0
        l = len(list)
        for ticker in list:
            # TODO: add score
            try:
                sto = Stockalyzer(ticker, self.api)
                s = pd.Series([ticker,
                               sto.get_analysis(),
                               sto.getPrice(),
                               sto.getStopPrice(),
                               sto.getSellPrice(),
                               sto.get_score()], index=indx)
                i += 1
                print('{}/{}: {} at {}, {}'.format(i, l, s['Symbol'], s['Price'], s['Analysis']))
                s_list.append(s)
            except Exception as ex:
                print(ticker, ex)
        df = pd.concat(s_list, axis=1).T
        return df

    def getBuy(self):
        data = self.data
        df = data.loc[data['Analysis'] == 'Buy']
        return df