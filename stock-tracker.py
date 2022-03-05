#!/home/pi/Documents/Stock-tracker/stocktracker/bin/python3

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from email.message import EmailMessage
import smtplib
import pickle
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email import encoders
import telegram_send as ts
import logging
import robin_stocks as r

# Logging
logging.basicConfig(filename='stocktracker.log', encoding='utf-8', level=logging.INFO)

# Email
gmail_user = 'stocknomitron@gmail.com' #os.environ['GMAIL_USER']
gmail_password = 'Stock$$69420' #os.environ['GMAIL_PASSWORD']

to_list = ['niallcdevlin@gmail.com'] #[os.environ['TO_LIST']]

# Stock lists
stock_list = ['MSFT', 'VOO', 'VTI', 'COST', 'AMZN', 'AAPL', 'BAC']
# 0 - Buy, 1 - Sell, 2 - Both
autotrade_stocks = {'MSFT':{'trade_type':2, 'trade_amount':1},
                    'VOO':{'trade_type':1, 'trade_amount':1}}
tickers = []
stock_status = {}
important_updates = {}

# Create stock tickers, get history, calculate stats
for stock in stock_list:
	current_ticker = yf.Ticker(stock)
	tickers.append(current_ticker)
	hist = current_ticker.history(period='1y', interval='1h')
	hist_close = hist['Close']
	avg_20 = hist_close.tail(n=20).mean()
	avg_50 = hist_close.tail(n=50).mean()
	last_50 = hist_close.tail(n=50)
	last_50.plot(label="{} last 50 day data".format(stock))

	# Compare stats
	if avg_20 > avg_50:
		color = 'g'
	else:
		color = 'r'

	# Get old stats
	try:
		with open('{}.pkl'.format(stock), 'rb') as f:
			old_stats = pickle.load(f)
			f.close()
	except:
		old_stats = ""
	# Dump new ones
	stats = {'avg_20':avg_20, 'avg':avg_50, '{}_diff'.format(stock):avg_20 - avg_50}
	with open('{}.pkl'.format(stock), 'wb') as f:
		pickle.dump(stats, f)
		f.close()

	plt.axhline(y=avg_20, color=color, linestyle='-', label='20 day average')
	plt.axhline(y=avg_50, color='b', linestyle='-', label='50 day average')
	plt.xlabel("Date")
	plt.ylabel("Price")
	plt.title("{} Stock Data".format(stock))
	plt.legend(loc='upper left')
	plt.savefig('{}.png'.format(stock))
	plt.clf()

	# 0 down 1 up
	old_trend = 0
	new_trend = 0
	email_msg = "Heres some text so we dont look like scammers"

	if (old_stats):
		if(old_stats['{}_diff'.format(stock)] > 0):
			old_trend = 1
		if(stats['{}_diff'.format(stock)] > 0):
			new_trend = 1

		if (old_trend == new_trend):
			if (new_trend == 1):
				print(f"{stock} rising")
				stock_status[stock] = f"{stock} rising"
			else:
				print(f"{stock} falling")
				stock_status[stock] = f"{stock} falling"
		else:
			b_or_s = ""
			if (old_trend == 0 and new_trend == 1):
				if stock in autotrade_stocks and autotrade_stocks[stock]['trade_type'] in (0, 2):
                    r.order_buy_market(stock, autotrade_stocks[stock]['trade_amount'])
                    b_or_s = "Bought"
                 else:
                 	b_or_s = "Buy"
			elif(old_trend == 1 and new_trend == 0):
				if stock in autotrade_stocks and autotrade_stocks[stock]['trade_type'] in (1, 2):
                    r.order_sell_market(stock, autotrade_stocks[stock]['trade_amount'])
                    b_or_s = "Sold"
                 else:
                 	b_or_s = "Sell"
			msg = "{} {} at {:.2f}".format(b_or_s, stock, current_ticker.info['currentPrice'])
			important_updates[stock] = msg
			print(msg)

	if (old_stats):
		if(old_stats['{}_diff'.format(stock)] > 0):
			old_trend = 1
		if(stats['{}_diff'.format(stock)] > 0):
			new_trend = 1
		if (old_trend == new_trend):
			if (new_trend == 1):
				print(f"{stock} rising")
				stock_status[stock] = f"{stock} rising"
			else:
				print(f"{stock} falling")
				stock_status[stock] = f"{stock} falling"
		else:
			if old_trend == 0 and new_trend == 1:
                print("Buy {} at {:.2f}".format(stock, current_ticker.info['currentPrice'])
                # Email
                
                    important_updates[stock] = "Bought {} at {:.2f}".format(stock, current_ticker.info['currentPrice'])
                else:
                    important_updates[stock] = "Buy {} at {:.2f}".format(stock, current_ticker.info['currentPrice'])
			elif old_trend == 1 and new_trend == 0:
				print("Sell {} at {:.2f}".format(stock, current_ticker.info['currentPrice']))
				# Email
                
				    important_updates[stock] = "Sold {} at {:.2f}".format(stock, current_ticker.info['currentPrice'])
                else:
                    important_updates[stock] = "Sell {} at {:.2f}".format(stock, current_ticker.info['currentPrice'])

r.export_completed_stock_orders(".")
sent_from = gmail_user
subject = 'Stock Status Update'
body = ""
if important_updates:
    messages = []
    body += "Important Updates (Buy/Sell)\n\n"
    for stock in important_updates:
        messages.append(important_updates[stock])
        body += important_updates[stock]
        body += "\n"
    ts.send(messages=messages)

body += "\n\nOther Stocks (Rising/Falling) Skip to the end for charts (see attachments)\n\n"
for stock in stock_status:
	body += stock_status[stock]
	body += "\n"

for to in to_list:
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sent_from
    msg['To'] = to

    txt = MIMEText(body)
    msg.attach(txt);

    for stock in stock_list:
        # set attachment mime and file name, the image type is png
        stock_img_file = f"{stock}.png"
        with open(stock_img_file, 'rb') as f:
            mime = MIMEImage(f.read(), name=os.path.basename(stock_img_file))
            # add required header data:
            mime.add_header('Content-Disposition', 'attachment', filename=stock_img_file)
            mime.add_header('X-Attachment-Id', '0')
            mime.add_header('Content-ID', '<0>')
            # encode with base64
            encoders.encode_base64(mime)
            # add MIMEBase object to MIMEMultipart object
            msg.attach(mime)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(gmail_user, gmail_password)
    s.sendmail(gmail_user, to, msg.as_string())
    s.quit()
    print("Email sent to", to)
    logging.info(f"Email sent to {to}")
