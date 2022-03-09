import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class DayTrader:
	def __init__(self, stock):
		self.stock = stock
		self.ticker = yf.Ticker(self.stock)
		self.history = self.ticker.history()