#!./stracker/bin/python3
import yahoo_fin.stock_info as yf
import pandas as pd
from stock_analyzer import Stockalyzer
import logging

class Screener:
    def __init__(self, verbose=False):
        self.verbose = verbose
        logging.basicConfig(filename='/var/www/html/log/screener.log',
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        msg = 'Getting stock list'
        logging.info(msg)
        if verbose:
            print(msg)
        self.list = yf.tickers_sp500()
        self.data = self.getData()
        self.buy = self.getBuy()

    def getData(self):
        msg = 'Evaluating stock list'
        logging.info(msg)
        if self.verbose:
            print(msg)
        list = self.list
        indx = ['Symbol', 'Analysis', 'Price', 'ADR', 'Score']
        s_list = []
        i = 0
        l = len(list)
        for ticker in list:
            try:
                sto = Stockalyzer(ticker)
                if sto.getPrice() < 250:
                    s = pd.Series([ticker,
                                   sto.get_analysis(),
                                   sto.getPrice(),
                                   sto.getADR(),
                                   sto.get_score()], index=indx)
                    i += 1
                    percent_done = round((i / l) * 100, 2)
                    msg = '{}% {} at ${:.2f}, {}'.format(percent_done, s['Symbol'], s['Price'], s['Analysis'])
                    logging.info(msg)
                    if self.verbose:
                        print(msg)
                    s_list.append(s)
            except Exception as ex:
                msg = '{} {}'.format(ticker, ex)
                logging.error(msg)
                if self.verbose:
                    print(msg)
        
        df = pd.concat(s_list, axis=1).T
        print('100% Total in list: {}'.format(len(df.index)))
        return df

    def getBuy(self):
        data = self.data
        df = data.loc[data['Analysis'] == 'Buy']
        return df
