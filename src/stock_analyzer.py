import numpy as np
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import yahoo_fin.stock_info as yf
from dotenv import load_dotenv
import json
import os
import ta

class Stockalyzer:
    def __init__(self, symbol, interval='day', mode='store', financials=True):
        '''
        Class to analyze stocks using 3 tecnical indicators: Relative Strength Index (RSI)
        Stochastic Oscillator, and Moving Average Convergence Divergence (MACD) and simple moving
        average analysis. Also performs basic finance analysis of the company and assigns score
        Params: ticker - 4 letter stock name eg. 'MSFT'
                interval='daily'
        '''
        load_dotenv()
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config = dir_path + "/config.json"
        with open(config, "r") as f:
            self.params = json.load(f)

        self.stock = symbol
        
        # Be sure to change keys in .env file if changing from paper/live
        self.api = tradeapi.REST(os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY'), os.getenv('APCA_ENDPOINT'))
        self.account = self.api.get_account()
        
        if interval == 'day':
            self.interval = tradeapi.TimeFrame.Day
        elif interval == 'hour':
            self.interval = tradeapi.TimeFrame.Hour
        else:
            raise ValueError("Interval must be 'hour' or 'day'")

        start = datetime.today().strftime('%Y-%m-%d')
        end = (datetime.today() - timedelta(200)).strftime('%Y-%m-%d')
        self.price_data = self.getPriceData(end, start)
        
        if self.price_data.empty:
            raise AttributeError('No Price Data found for {}'.format(self.stock))
        
        self.price = self.getPrice()
        self.adr = self.getADR()
        self.avg_50 = self.price_data['close'].tail(50).mean()
        self.avg_200 = self.price_data['close'].tail(200).mean()

        self.rsi = ta.momentum.RSIIndicator(self.price_data['close'], 7).rsi()
        
        stochastic = ta.momentum.StochasticOscillator(self.price_data['high'], self.price_data['low'], self.price_data['close'])
        self.stoch = stochastic.stoch()
        self.stoch_sig = stochastic.stoch_signal()
        
        macd = ta.trend.MACD(self.price_data['close'])
        self.macd = macd.macd()
        self.macd_sig = macd.macd_signal()
        
        self.financials = financials

        if self.financials:
            self.balance_sheet = yf.get_balance_sheet(self.stock)
            self.income_statement = yf.get_income_statement(self.stock)
            self.cfs = yf.get_cash_flow(self.stock)
            self.years = self.balance_sheet.columns
        
        self.score = self.get_score()
        self.analysis = self.get_analysis()

    def getPriceData(self, start, end):
        df = self.api.get_bars(self.stock, self.interval, start, end, adjustment='raw').df
        return df
    
    def getPrice(self):
        return self.price_data['close'].iloc[-1]

    def getADR(self):
        # Average Daily Range
        data = self.price_data.tail(self.params['technical_params']['ADR']['period'])
        
        ranges = data['high'] - data['low']
        
        return ranges.mean()

    def getStopPrice(self):
        return self.price - self.adr

    def getSellPrice(self):
        return self.price + self.adr * 2

    def profitability(self):
        """
        Determine profitability of a company using income statement, balance sheet, and cash flow
        :return: p_score - total profitability score from 0 to 4
        """

        if not self.financials:
            raise Exception("Financials must be enabled. Set financials argument to true when initializing Stockalyzer")

        p_score = 0

        # Net Income
        net_income = self.income_statement[self.years[0]]['netIncome']
        net_income_last = self.income_statement[self.years[1]]['netIncome']
        ni_ratio_score = 1 if net_income > net_income_last and net_income > 0 else 0
        p_score += ni_ratio_score

        # Operating Cash Flow
        op_cf = self.cfs[self.years[0]]['totalCashFromOperatingActivities']
        of_cf_score = 1 if op_cf > 0 else 0
        p_score += of_cf_score

        # Return on Assets
        avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]]['totalAssets']) / 2
        avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]]['totalAssets']) / 2
        RoA = net_income / avg_assets
        RoA_last = net_income_last / avg_assets_last
        RoA_score = 1 if RoA > RoA_last else 0
        p_score += RoA_score

        # Accruals
        total_assets = self.balance_sheet[self.years[0]]['totalAssets']
        accruals = op_cf / total_assets - RoA
        acc_score = 1 if accruals > 0 else 0
        p_score += acc_score

        return p_score

    def leverage(self):
        """
        Determine leverage of a company with balance sheet
        :return: l_score - total leverage score from 0 to 2
        """
        
        if not self.financials:
            raise Exception("Financials must be enabled. Set financials argument to true when initializing Stockalyzer")

        l_score = 0

        # Long-term debt ratio
        try:
            ltd = self.balance_sheet[self.years[0]]['longTermDebt']
            total_assets = self.balance_sheet[self.years[0]]['totalAssets']
            debt_ratio = ltd / total_assets
            dr_score = 1 if debt_ratio < 0.4 else 0
            l_score += dr_score
        except:
            l_score += 1

        # Current ratio
        current_assets = self.balance_sheet[self.years[0]]['totalCurrentAssets']
        current_liab = self.balance_sheet[self.years[0]]['totalCurrentLiabilities']
        current_ratio = current_assets / current_liab
        cr_score = 1 if current_ratio > 1 else 0
        l_score += cr_score

        return l_score

    def operating_efficiency(self):
        """
        Determine operating efficency of a company
        :return: oe_score - score representing operating efficency from 0 to 2
        """
        
        if not self.financials:
            raise Exception("Financials must be enabled. Set financials argument to true when initializing Stockalyzer")

        oe_score = 0

        # Gross margin
        gp = self.income_statement[self.years[0]]['grossProfit']
        gp_last = self.income_statement[self.years[1]]['grossProfit']
        revenue = self.income_statement[self.years[0]]['totalRevenue']
        revenue_last = self.income_statement[self.years[1]]['totalRevenue']
        gm = gp / revenue
        gm_last = gp_last / revenue_last
        gm_score = 1 if gm > gm_last else 0
        oe_score += gm_score

        # Asset turnover
        avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]]['totalAssets']) / 2
        avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]]['totalAssets']) / 2
        at = revenue / avg_assets
        at_last = revenue_last / avg_assets_last
        at_score = 1 if at > at_last else 0
        oe_score += at_score

        return oe_score

    def get_score(self):
        """
        Returns total score based on profitability, leverage, and operating efficiency
        :return: s - total score from 0 (worst) to 8 (best)
        """
        
        if not self.financials:
            raise Exception("Financials must be enabled. Set financials argument to true when initializing Stockalyzer")

        s = self.profitability() + self.leverage() + self.operating_efficiency()
        return s

    def get_analysis(self, timestamp='now'):
        '''
        Returns an analysis of given stock in terms of a buy,
        sell, or hold position. Estimated 9% gain
        Return: string 'Buy', 'Sell', or 'Hold'
        '''
        rsi = self.rsi.iloc[-1] > 50
        stoch = self.stoch.iloc[-1] > self.stoch_sig.iloc[-1]
        macd = self.macd.iloc[-1] > self.macd_sig.iloc[-1]
        up = self.price > self.avg_50 and self.avg_50 > self.avg_200

        if (rsi and
            stoch and
            macd and
            up):
            return 'Buy'
        elif (not rsi and
              not stoch and
              not macd and
              not up):
            return 'Sell'
        else:
            return 'Hold'
