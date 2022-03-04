import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from email.message import EmailMessage
import smtplib
import pickle

# Email
strFrom = 'niallcdevlin@gmail.com'
strTo = 'niallcdevlin@gmail.com'

# Create stock tickers, get history, calculate stats
msft = yf.Ticker("MSFT")
msft_hist = msft.history(period='1y', interval='1h')
msft_hist_close = msft_hist['Close']
msft_20_avg = msft_hist_close.tail(n=20).mean()
msft_50_avg = msft_hist_close.tail(n=50).mean()
msft_last_50 = msft_hist_close.tail(n=50)
msft_last_50.plot(label="msft last 50 day data")

# Compare stats
if msft_20_avg > msft_50_avg:
	color = 'g'
else:
	color = 'r'

# Get old stats
with open('stats.pkl', 'rb') as f:
	old_stats = pickle.load(f)
	f.close()
# Dump new ones
stats = {'msft_20_avg':msft_20_avg, 'msft_50_avg':msft_50_avg, 'msft_diff':msft_20_avg - msft_50_avg}
with open('stats.pkl', 'wb') as f:
	pickle.dump(stats, f)
	f.close()

plt.axhline(y=msft_20_avg, color=color, linestyle='-', label='msft 20 day average')
plt.axhline(y=msft_50_avg, color=color, linestyle='-', label='msft 50 day average')
plt.savefig('msft.png')

# 0 down 1 up
old_trend = 0
new_trend = 0

if (old_stats):
	if(old_stats['msft_diff'] > 0):
		old_trend = 1
	if(stats['msft_diff'] > 0):
		new_trend = 1
	if (old_trend == new_trend):
		if (new_trend == 1):
			print("MSFT rising")
		else:
			print("MSFT falling")
	else:
		if (old_trend == 0 and new_trend == 1):
			print("Buy MSFT at {:.2f}".format(msft.info['currentPrice']))
			# Email
		elif(old_trend == 1 and new_trend == 0):
			print("Sell MSFT at {:.2f}".format(msft.info['currentPrice']))
			# Email