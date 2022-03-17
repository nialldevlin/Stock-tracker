#!/home/pi/Documents/Stock-tracker/stocktracker/bin/python3\
from stock_analyzer import Stockalyzer
import yfinance as yf
stock = 'MSFT'
tick = yf.Ticker(stock)
hist = tick.history(period='1y', interval='1h')
s = Stockalyzer('MSFT', tick, hist)
print(s.tiaanalysis(mode='store'))
balance, num_stock = s.runSimulationTI(1000, 1, verbose=True)
total = balance + num_stock * tick.info['currentPrice']
print("{} 100d Simulation: Final balance: {}, Final stock {}, Total: {}".format(stock, balance, num_stock, total))