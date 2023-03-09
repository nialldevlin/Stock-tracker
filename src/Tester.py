#!./stracker/bin/python3
from trader import Trader
import pandas as pd
import sqlite3

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = r"/var/www/html/stockdb.sqlite"
    conn = sqlite3.connect(db)
    df = pd.read_sql('SELECT * FROM stockdb', conn)
    buy_list = df.loc[df['Analysis'] == 'Buy']
    sell_list = df.loc[df['Analysis'] == 'Sell']
    trader = Trader(buy_list, sell_list)
    p = trader.evalPositions()
    if len(buy_list.index) >= len(sell_list.index):
        trader.buyPositions(p)
    else:
        trader.shortPositions(p)
