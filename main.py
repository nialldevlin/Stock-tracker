#!./stracker/bin/python3
from screener import Screener
from trader import Trader
import logging

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    s = Screener()
    trader = Trader(s.buy, s.sell)
    p = trader.evalPositions()
    if s.buy_or_sell() == 'Buy':
        trader.buyPositions(p)
    else:
        trader.shortPositions(p)
