#!./stracker/bin/python3
import yahoo_fin.stock_info as yf
import pandas as pd
from stock_analyzer import Stockalyzer
import logging
import sqlite3
import os
import json

class Screener:
    def __init__(self, verbose=False):
        self.verbose = verbose
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = dir_path + "/config.json"
        print(config)
        with open(config, "r") as f:
            self.params = json.load(f)
        logging.basicConfig(filename=self.params['screener_log'],
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.conn = sqlite3.connect(self.params['db_file'])
        msg = 'Getting stock list'
        logging.info(msg)
        if verbose:
            print(msg)
        self.list = yf.tickers_sp500()
        self.data = self.getData()
        self.buy = self.getBuy()
    
    def createDBTable(self, columns):
        sql = "CREATE TABLE IF NOT EXISTS stockdb ("
        sql += columns[0]
        sql += " PRIMARY KEY, "
        sql += ", ".join(columns[1:])
        sql += ')'
        c = self.conn.cursor()
        c.execute(sql)
    
    def seriesToDB(self, series):
        sql = "INSERT OR REPLACE INTO stockdb ("
        sql += ", ".join(series.keys().to_list())
        sql += ") VALUES ("
        sql += ", ".join(['?' for i in range(len(series.values))])
        sql += ")"
        c = self.conn.cursor()
        c.execute(sql, tuple(series.values))

    def getData(self):
        msg = 'Evaluating stock list'
        logging.info(msg)
        if self.verbose:
            print(msg)
        list = self.list
        indx = ['Symbol', 'Analysis', 'Price', 'ADR', 'Score']
        self.createDBTable(indx)
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
                    self.seriesToDB(s)
                    s_list.append(s)
                    
                    i += 1
                    percent_done = round((i / l) * 100, 2)
                    msg = '{}% {} at ${:.2f}, {}'.format(percent_done, s['Symbol'], s['Price'], s['Analysis'])
                    logging.info(msg)
                    if self.verbose:
                        print(msg)
            except Exception as ex:
                msg = '{} {}'.format(ticker, ex)
                logging.error(msg)
                if self.verbose:
                    print(msg)
        
        df = pd.concat(s_list, axis=1).T
        #df.to_sql('stockdb', con=self.conn, if_exists='replace')
        print('100% Total in list: {}'.format(len(df.index)))
        return df

    def getBuy(self):
        data = self.data
        df = data.loc[data['Analysis'] == 'Buy']
        return df
