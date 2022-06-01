#!./stracker/bin/python3
import yahoo_fin.stock_info as yf
import pandas as pd
from stock_analyzer import Stockalyzer
import logging
import sqlite3
import os
import json

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)
    return logging.getLogger(logger_name)

class Screener:
    def __init__(self, verbose=False):
        self.verbose = verbose
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = dir_path + "/config.json"
        with open(config, "r") as f:
            self.params = json.load(f)
        self.log_s = setup_logger('screener', self.params['screener_log'])
        self.conn = sqlite3.connect(self.params['db_file'])
        msg = 'Getting stock list'
        self.log_s.info(msg)
        if verbose:
            print(msg)
        self.list = yf.tickers_sp500()
        self.data = self.getData()
        self.buy = self.getBuy()
    
    def createDatabase(self, columns):
        c = self.conn.cursor()
        sql = "CREATE TABLE IF NOT EXISTS stockdb ("
        sql += columns[0]
        sql += " PRIMARY KEY, "
        sql += ", ".join(columns[1:])
        sql += ')'
        
        c.execute(sql)
        sql =   """CREATE TABLE IF NOT EXISTS modifications (
                    table_name TEXT NOT NULL PRIMARY KEY ON CONFLICT REPLACE,
                    action TEXT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );"""
        c.execute(sql)
        
        sql =   """CREATE TRIGGER IF NOT EXISTS table1_ondelete AFTER DELETE ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','DELETE');
                END;"""
        c.execute(sql)
        
        c.execute(sql)

        sql =   """CREATE TRIGGER IF NOT EXISTS table1_onupdate AFTER UPDATE ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','UPDATE');
                END;"""
        c.execute(sql)

        sql =   """CREATE TRIGGER IF NOT EXISTS table1_oninsert AFTER INSERT ON stockdb
                BEGIN
                    INSERT INTO modifications (table_name, action) VALUES ('stockdb','INSERT');
                END;"""
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
        self.log_s.info(msg)
        if self.verbose:
            print(msg)
        list = self.list
        indx = ['Symbol', 'Analysis', 'Price', 'ADR', 'Score', 'RSI', 'MACD', 'MACD_SIG', 'STOCH']
        self.createDatabase(indx)
        s_list = []
        i = 0
        l = len(list)
        for ticker in list:
            try:
                sto = Stockalyzer(ticker)
                if sto.getPrice() < 250:
                    row = [ticker,
                        sto.analysis,
                        round(sto.price, 2),
                        round(sto.adr, 2),
                        sto.score,
                        round(sto.rsi, 2),
                        round(sto.macd, 2),
                        round(sto.macd_sig, 2),
                        round(sto.stochk, 2)]
                    s = pd.Series(row, index=indx)
                    #self.seriesToDB(s)
                    s_list.append(s)
                    
                    i += 1
                    percent_done = round((i / l) * 100, 2)
                    msg = '{}% {} at ${:.2f}, {}'.format(percent_done, s['Symbol'], s['Price'], s['Analysis'])
                    self.log_s.info(msg)
                    if self.verbose:
                        print(msg)
            except Exception as ex:
                msg = '{} {}'.format(ticker, ex)
                self.log_s.error(msg)
                if self.verbose:
                    print(msg)
        
        df = pd.concat(s_list, axis=1).T
        df.to_sql('stockdb', con=self.conn, if_exists='replace')
        print('100% Total in list: {}'.format(len(df.index)))
        return df

    def getBuy(self):
        data = self.data
        df = data.loc[data['Analysis'] == 'Buy']
        return df
