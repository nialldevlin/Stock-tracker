#!./stracker/bin/python3
import pandas as pd
from stock_analyzer import  Stockalyzer
import alpaca_trade_api as tradeapi
from screener import Screener
import sqlite3
import re
from dotenv import load_dotenv
import os
import logging

class Trader:
    def __init__(self):
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
        db = r"stockdb.sqlite"
        conn = sqlite3.connect(db)
        c = conn.cursor()
        df = pd.read_sql('SELECT * FROM stockdb', conn)
        
        buy_list = df.loc[df['Analysis'] == 'Buy']
        buying_power = float(self.account.buying_power)
        buy_list = buy_list.loc[buy_list['Score'] == 8].sort_values(by=['Price'])
        best_stock = None
        if len(buy_list.index) == 0:
            logging.info('No stocks found to buy')
            return "No Stocks Found"
        
        for i in range(len(buy_list.index)):
            print(buy_list.iloc[i])
            analysis = Stockalyzer(buy_list.iloc[i]['Symbol']).get_analysis()
            if analysis == 'Buy':
                best_stock = buy_list.iloc[i]
                print(best_stock)
                break
        if best_stock == None:
            logging.info('No stocks found to buy')
            return "No Stocks Found"
        buy_price = round(best_stock['Price'], 2)
        tp_price = round(best_stock['Sell'], 2)
        stop_price = round(best_stock['Stop'], 2)
        logging.info('Best stock found:')
        buy_amount = int(buying_power / buy_price)
        logging.info(best_stock)
        
        self.api.submit_order(best_stock['Symbol'],
                              qty=buy_amount,
                              side='buy',
                              type='market',
                              time_in_force='day',
                              order_class='bracket',
                              take_profit={'limit_price':tp_price},
                              stop_loss={'stop_price':stop_price,
                              'limit_price':stop_price})
    
        return best_stock
