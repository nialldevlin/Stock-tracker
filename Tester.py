#!./stracker/bin/python3
from trader import Trader

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    trader = Trader()
    print(trader.evalPositions())
    print(trader.buyPositions())
