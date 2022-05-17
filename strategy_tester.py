from stock_analyzer import  Stockalyzer
from datetime import datetime

class powerXTester:
    def __init__(self, ticker):
        self.sa = Stockalyzer(ticker)

    def runSimulation(self, starting_cash, buy_amount):
        balance = starting_cash
        stocks = 0
        #b_or_s = True # False last bought, True last sold
        for i in self.sa.price_data.index:
            if self.sa.rsi_data.loc[i] > 50 and self.sa.stochk_data.loc[i] > 50 and self.sa.macd_data.loc[i] > self.sa.macd_sig_data.loc[i]:
                if balance > buy_amount * self.sa.price_data['Open'].loc[i]:
                    balance -= buy_amount * self.sa.price_data['Open'].loc[i]
                    stocks += buy_amount
            else:
                if stocks > 0:
                    balance += buy_amount * self.sa.price_data['Open'].loc[i]
                    stocks -= buy_amount
        if stocks > 0:
            balance += stocks * self.sa.price
        return balance

