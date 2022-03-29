#!../stracker/bin/python3
from stock_analyzer import Stockalyzer
stock = 'VTI'
s = Stockalyzer(stock, interval='60min')
#print(s.analysis)
#s.saveAsPng()
s.display()
"""print(s.tiaanalysis(mode='store'))
balance, num_stock = s.runSimulationTI(1000, 1, verbose=True)
total = balance + num_stock * tick.info['currentPrice']
print("{} 100d Simulation: Final balance: {}, Final stock {}, Total: {}".format(stock, balance, num_stock, total))"""
