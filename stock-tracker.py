#!/home/pi/Documents/Stock-tracker/stocktracker/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email import encoders
import telegram_send as ts
import logging
import robin_stocks as r
from stock_analyzer import Stockalyzer
from datetime import datetime

# Logging
logging.basicConfig(filename='stocktracker.log', encoding='utf-8', level=logging.INFO)

# Email
gmail_user = 'stocknomitron@gmail.com' #os.environ['GMAIL_USER']
gmail_password = 'Stock$$69420' #os.environ['GMAIL_PASSWORD']

to_list = ['niallcdevlin@gmail.com'] #[os.environ['TO_LIST']]

# Stock lists
stock_list = np.array(['MSFT', 'VOO', 'VTI', 'COST', 'AMZN', 'AAPL', 'BAC'])
# 0 - Buy, 1 - Sell, 2 - Both
autotrade_stocks = {'MSFT':{'trade_type':2, 'trade_amount':1},
                    'VOO':{'trade_type':2, 'trade_amount':1}
                    'VTI':{'trade_type':2, 'trade_amount':1}}
autotrade = False
tickers = np.array()
stock_status = {}
robin_actions = {}

# Create stock tickers, get history run analysis
for stock in stock_list:
	current_ticker = yf.Ticker(stock)
	tickers.append(current_ticker)
	hist = current_ticker.history(period='1y', interval='1h')
	stockbot = Stockalyzer(stock, current_ticker, hist)
	analysis = stockbot.getAnalysis()
	price = stockbot.getCurrentPrice()
	stockbot.saveAsPng(f"{stock}.png")
	stock_status[stock] = {'analysis':analysis, 'price':price}

	if autotrade:
		if analysis = 'Buy':
				if stock in autotrade_stocks and autotrade_stocks[stock]['trade_type'] in (0, 2):
					r.order_buy_market(stock, autotrade_stocks[stock]['trade_amount'])
					robin_actions[stock] = "Bought"
					logging.info("Bought {}".format(stock))
		elif analysis = 'Sell':
				if stock in autotrade_stocks and autotrade_stocks[stock]['trade_type'] in (1, 2):
					r.order_sell_market(stock, autotrade_stocks[stock]['trade_amount'])
					robin_actions[stock] = "Sold"
					logging.info("Sold {}".format(stock))

r.export_completed_stock_orders(".")
sent_from = gmail_user
subject = 'Stock Status Update'
body = "Stockalyzer analysis at {} \n\n".format(datetime.now().strftime("%A, %B %d %H:%M"))

messages = []
for stock in stock_status:
	analysis = stock_status[stock]['analysis']
	price = stock_status[stock]['price']
	stock_line = "{} {} at {}\n".format(analysis, stock, price)
	body += stock_line
	if analysis in ('Buy', 'Sell'):
		messages.append(stock_line)

ts.send(messages=messages)

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
