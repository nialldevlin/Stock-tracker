#!./stracker/bin/python3
import pandas as pd
from stock_analyzer import  Stockalyzer
import alpaca_trade_api as tradeapi
import sqlite3
import re
from dotenv import load_dotenv
import os
import logging

class Trader:
    def __init__(self, buy_list=None):
        logging.basicConfig(filename='/var/www/html/log/trader.log',
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        load_dotenv()
        live_trading = 'https://api.alpaca.markets'
        paper_trading = 'https://paper-api.alpaca.markets'
        self.api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), paper_trading)
        self.account = self.api.get_account()
        self.positions = self.api.list_positions()
        
        if buy_list != None:
            self.buy_list = buy_list
        else:
            db = r"/var/www/html/stockdb.sqlite"
            conn = sqlite3.connect(db)
            df = pd.read_sql('SELECT * FROM stockdb', conn)
            self.buy_list = df.loc[df['Analysis'] == 'Buy']

    def evalPositions(self):
        orders = []
        for pos in self.positions:
            symbol = pos.symbol.strip()
            s = Stockalyzer(symbol)
            logging.info('{}: {}'.format(symbol, s.get_analysis()))
            if s.get_analysis() != 'Buy':
                orders = self.api.list_orders()
                for order in orders:
                    if order.symbol == symbol:
                        self.api.cancel_order(order.id)
                self.api.submit_order(symbol, qty=pos.qty, side='sell', type='market')
                logging.info('Sold {}'.format(symbol))
                orders.append(symbol)
        return orders

    def buyPositions(self):
        buying_power = float(self.account.buying_power)
        self.buy_list = self.buy_list.loc[self.buy_list['Score'] == 8].sort_values(by=['Price'])
        
        best_stock = pd.Series([])
        bse = False
        s = None
        
        if len(self.buy_list.index) == 0:
            logging.info('No stocks found to buy')
            return "No Stocks Found"
        
        for i in range(len(self.buy_list.index)):
            s = Stockalyzer(self.buy_list.iloc[i]['Symbol'])
            analysis = s.get_analysis()
            if analysis == 'Buy':
                best_stock = self.buy_list.iloc[i]
                bse = True
                break
        
        if not bse:
            logging.info('No stocks found to buy')
            return "No Stocks Found"
        
        adr = best_stock['ADR']
        buy_price = round(s.getPrice(), 2)
        tp_price = round(buy_price + adr * 2, 2)
        stop_price = round(buy_price - adr, 2)
        logging.info('Best stock found:')
        buy_amount = int(buying_power / (buy_price + adr))
        buy_amount = buy_amount if buy_amount < 100 else 100
        logging.info(best_stock)
        
        self.api.submit_order(best_stock['Symbol'],
                              qty=buy_amount,
                              side='buy',
                              type='market',
                              time_in_force='gtc',
                              order_class='bracket',
                              take_profit={'limit_price':tp_price},
                              stop_loss={'stop_price':stop_price,
                              'limit_price':stop_price})
    
        return best_stock
