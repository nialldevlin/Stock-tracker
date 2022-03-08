import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

stock = 'MSFT'
ticker = yf.Ticker(stock)
"""
change_points = {}
last_price = 0
current_price = 0
status = False # false falling true rising
last_status = False # false falling true rising
# get all change points 
for price in hist_close:
	last_price = current_price
	current_price = price
	
print('Current balance : ${}'.format(curr_balance))
print('Buy and sell points')
for p in b_s_points:
	if p == 'b':
		print('Bought at ${}'.format(b_s_points[p]))
	elif p == 'nb':
		print('Not bought at ${} (insufficient funds)'.format(b_s_points[p]))
	elif p == 's':
		print('Sold at ${}'.format(b_s_points[p]))
	elif p == 'ns':
		print('Not sold at ${} (no stock)'.format(b_s_points[p]))
hist_close.plot(label="{} last 1y day data".format(stock))
plt.legend(loc='upper left')
plt.show()
plt.clf()"""