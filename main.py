#!./stracker/bin/python3
from trader import Trader
import logging

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    trader = Trader()
    trader.evalPositions()
    trader.buyPositions()
