#!./stracker/bin/python3
from trader import Trader
import logging

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	trader = Trader()
    logging.basicConfig(filename='log/screener.log', encoding='utf-8', level=logging.INFO)
	logging.info('Evaluating current info')
	logging.info(trader.evalinfo())
	logging.info('Evaluating new info')
	logging.info(trader.buyinfo())
