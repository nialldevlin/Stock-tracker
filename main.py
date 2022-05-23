#!./stracker/bin/python3
from trader import Trader
import logging

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    trader = Trader()
    logging.basicConfig(filename='log/main.log',
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
                        logging.info('Getting stock list')
    logging.info('Evaluating current info')
    logging.info(trader.evalinfo())
    logging.info('Evaluating new info')
    logging.info(trader.buyinfo())
