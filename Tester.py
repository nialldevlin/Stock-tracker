from screener import Screener
from strategy_tester import runSimulation
import alpaca_trade_api as tradeapi

api = tradeapi.REST('AKO60D937GTSFKPNEWEI', 'rstzhpuuGzhBpJ3ojwT4oswGybvBJcOcfGEpGKwr', 'https://api.alpaca.markets')
screener = Screener(api)
best_stock = ''
best_balance = 0
init_balance = 1000
verbose = True

for stock in screener.data['Symbol']:
    balance = runSimulation(stock, init_balance, api, verbose)
    print(stock, balance)
    if balance > best_balance:
        best_stock = stock
        best_balance = balance
    if verbose:
        print()
        print()
print('Best: ', best_stock, best_balance)