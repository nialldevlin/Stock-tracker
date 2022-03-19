#!~/anaconda3/bin/python

import matplotlib.pyplot as plt
import numpy as np
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email import encoders
import telegram_send as ts
import logging
import robin_stocks.robinhood as r
from datetime import datetime
import argparse
import yfinance as yf
import os
import smtplib
import time

from stock_analyzer import Stockalyzer
from password_handler import PasswordHandler

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', default=0)
args = parser.parse_args()

# Logging
logging.basicConfig(filename='stocktracker.log', encoding='utf-8', level=logging.INFO)

# Retrieve stored passwords
ph = PasswordHandler()

# Email
gmail_user = 'stocknomitron@gmail.com'
ph.storePassword(gmail_user, 'Stock$$69420')
gmail_password = ph.getPassword(gmail_user)

to_list = ['niallcdevlin@gmail.com']

# Robinhood
r_user = 'devnomitron'
r_pass = ph.getPassword(r_user)
login = r.login(r_user,r_pass)

# Stock lists
stock_list = np.array(['MSFT', 'VOO', 'VTI', 'COST', 'AMZN', 'AAPL', 'BAC', 'AMD'])
stock_status = {}
# Create stock tickers, get history run analysis
for stock in stock_list:
	stockbot = Stockalyzer(stock, interval='60min')
	analysis = stockbot.analysis['analysis']
	price = stockbot.analysis['current price']
	stockbot.saveAsPng(f"{stock}.png")
	stock_status[stock] = {'analysis':analysis, 'price':price}

	if args.verbose == 1:
		print(f"{analysis} {stock} at {price}")

	if args.verbose == 2:
		stockbot.display()

	time.sleep(60)

sent_from = gmail_user
subject = 'Stock Status Update'
body = "Stockalyzer analysis at {} \n\n".format(datetime.now().strftime("%A, %B %d %H:%M"))

for stock in stock_status:
	analysis = stock_status[stock]['analysis']
	price = stock_status[stock]['price']
	stock_line = "{} {} at {:.2f}\n".format(analysis, stock, price)
	body += stock_line

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
		try:
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

		except Exception as ex:
			if args.verbose == 1:
				print(f"Failed to attach file {stock_img_file}")
				print(f"{ex}")
			logging.warning(f"Failed to attach file {stock_img_file}")
			logging.warning(f"{ex}")

	try:
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(gmail_user, gmail_password)
		s.sendmail(gmail_user, to, msg.as_string())
		s.quit()
		if args.verbose == 1:
			print(f"Email sent to {to} at {datetime.now()}")
		logging.info(f"Email sent to {to} at {datetime.now()}")
	except Exception as ex:
		logging.error(f"Failed to send email to {to} at {datetime.now()}")
		logging.warning(f"{ex}")
		if args.verbose == 1:
			print(f"Failed to send email to {to} at {datetime.now()}")
			print(f"{ex}")
