#!./stracker/bin/python3
import pandas as pd
from stock_analyzer import  Stockalyzer
import alpaca_trade_api as tradeapi
import sqlite3
import re
from dotenv import load_dotenv
import os
import logging
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

class Trader:
    def __init__(self, buy_list=pd.DataFrame({})):
        load_dotenv()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = dir_path + "/config.json"
        with open(config, "r") as f:
            self.params = json.load(f)
        self.log_t = setup_logger('trader', self.params['trader_log'])
        
        self.api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), os.getenv('APCA_ENDPOINT'))
        self.account = self.api.get_account()
        self.positions = self.api.list_positions()
        
        if not buy_list.empty:
            self.buy_list = buy_list
        else:
            db = self.params['db_file']
            conn = sqlite3.connect(db)
            df = pd.read_sql('SELECT * FROM stockdb', conn)
            self.buy_list = df.loc[df['Analysis'] == 'Buy']
        self.buy_list = self.buy_list.loc[self.buy_list['Score'] == 8].sort_values(by=['Price'])

    def evalPositions(self):
        positions = []
        self.log_t.info("Current Positions")
        for pos in self.positions:
            symbol = pos.symbol.strip()
            s = Stockalyzer(symbol)
            self.log_t.info('{}: {}'.format(symbol, s.get_analysis()))
            if s.get_analysis() != 'Buy':
                orders = self.api.list_orders()
                for order in orders:
                    if order.symbol == symbol:
                        self.api.cancel_order(order.id)
                self.api.submit_order(symbol, qty=pos.qty, side='sell', type='market')
                self.log_t.info('Sold {}'.format(symbol))
        
        for pos in self.api.list_positions():
            positions.append(pos.symbol.strip())
        return positions

    def buyPositions(self, positions):
        buying_power = float(self.account.buying_power)
        
        if len(self.buy_list.index) == 0:
            self.log_t.info('No stocks found to buy')
            return "No Stocks Found"
        
        orders = []
        total = 0
        
        for i in range(len(self.buy_list.index)):
            stock = self.buy_list.iloc[i]
            s = Stockalyzer(stock['Symbol'])
            analysis = s.get_analysis()
            if analysis == 'Buy' and stock['Symbol'] not in positions:
                buy_price = round(s.getPrice(), 2)
                
                total += buy_price
                orders.append([stock['Symbol'], buy_price])
        
        for order in orders:
            buy_amount = (order[1] / total) * buying_power
            try:
                self.api.submit_order(order[0],
                                      notional=buy_amount,
                                      side='buy',
                                      type='market',
                                      time_in_force='day')
                self.log_t.info('Buying {} of: {}'.format(order[1], order[0]))
            except Exception as ex:
                self.log_t.error(ex)
                print(ex)

        return orders
