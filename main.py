#!./stracker/bin/python3
from trader import Trader

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	trader = Trader()
	print('Evaluating current positions\n')
	print(trader.evalPositions())
	print('Evaluating new positions\n')
	print(trader.buyPositions())
