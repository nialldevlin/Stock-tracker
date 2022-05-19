from screener import Screener
from strategy_tester import runSimulation

screener = Screener()
best_stock = ''
best_balance = 0
init_balance = 1000
verbose = False

for stock in screener.data['Symbol']:
    balance = runSimulation(stock, init_balance, verbose)
    print(stock, balance)
    if balance > best_balance:
        best_stock = stock
        best_balance = balance
    if verbose:
        print()
        print()
print('Best: ', best_stock, best_balance)