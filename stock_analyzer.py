import numpy as np
import yfinance as yf
import yahoo_fin.stock_info as yfinfo
import pandas as pd


class Stockalyzer:
    """
    Analyzes stocks with technical data from YFinance library.
    Uses RSI, MACD, Stochastic, and ATR indicators.

    ...

    Methods
    -------
    __str__()
        Override tostring operator

    toSeries()
        Returns analysis and information in pandas series
    """

    def __init__(self, symbol, interval='1d'):
        """Set up data collection, download data

        :param symbol: Ticker symbol
        :param interval: Interval to get history
        """

        if interval == '1d':
            tpm = 1
        elif interval == '1h':
            tpm = 16
        else:
            raise AttributeError('Incorrect Interval. Possible Intervals: 1h 1d')

        self.params = {
            'RSI': {
                'interval': interval,
                'time_period': 7 * tpm,
                'series_type': 'close'
            },
            'STOCH': {
                'interval': interval,
                'fastkperiod': 14 * tpm,
                'slowkperiod': 3 * tpm,
                'slowdperiod': 3 * tpm
            },
            'MACDEXT': {
                'interval': interval,
                'series_type': 'close',
                'fastperiod': 12 * tpm,
                'slowperiod': 26 * tpm,
                'signalperiod': 9 * tpm,
                'fastmatype': 1,
                'slowmatype': 1,
                'signalmatype': 1
            },
            'ATR': {
                'interval': interval,
                'time_period': 7 * tpm
            }
        }

        self.stock = symbol
        self.ticker = yf.Ticker(self.stock)
        self.interval = interval

        self.price_data = self._getPriceData(interval)
        if self.price_data.empty:
            raise AttributeError('No Price Data found for {}'.format(self.stock))
        self.rsi_data = self._getRSIData()
        self.stochk_data, self.stochd_data = self._getStochData()
        self.macd_data, self.macd_sig_data = self._getMACDData()
        self.avg_50_data = self.price_data['Close'].rolling(50).mean()
        self.avg_200_data = self.price_data['Close'].rolling(200).mean()

        self.price = self._getPrice()
        self.rsi = self._getRSI()
        self.stochk, self.stochd = self._getStoch()
        self.macd, self.macd_sig = self._getMACD()
        self.adr = self._getADR()
        self.stop = self.price - self.adr
        self.sell = self.price + self.adr * 2
        self.avg_50 = self.avg_50_data.tail(1)[0]
        self.avg_200 = self.avg_200_data.tail(1)[0]

        """print("Here 0")
        self.balance_sheet = self.ticker.balance_sheet
        print("Here 1")
        self.income_statement = yfinfo.get_income_statement(self.stock)
        print("Here 2")
        self.cfs = yfinfo.get_cash_flow(self.stock)
        print("Here 3")
        self.years = self.balance_sheet.columns"""

        self.score = 0 #self._get_score()
        self.analysis = self._get_analysis()

    def __str__(self):
        """ToString operator"""

        return '{}\nPrice: ${:.2f}\nScore: {}\nAnalysis: {}'.format(self.stock, self.price, self.score, self.analysis)

    def toSeries(self):
        """Returns series with stock, analysis, price, stop price, limit price, and score"""

        return pd.Series([self.stock,
                          self.analysis,
                          self.price,
                          self.stop,
                          self.sell,
                          self.score], index=['Symbol', 'Analysis', 'Price', 'Stop', 'Limit', 'Score'])

    def _getPriceData(self, interval='1d'):
        """Download Price history"""

        return self.ticker.history(period='1y', interval=interval)

    def _getRSIData(self):
        """Calculate Relative Strength Index data"""

        rsi_period = 7
        change = self.price_data['Close'].diff()
        up = change.clip(lower=0)
        down = -1 * change.clip(upper=0)
        avgu = up.ewm(span=rsi_period, adjust=False).mean()
        avgd = down.ewm(span=rsi_period, adjust=False).mean()
        rs = avgu / avgd
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _getStochData(self):
        """Calculate Stochastic Oscillator data"""

        low_d = self.price_data['Low'].transform(lambda x: x.rolling(window=3).min())
        high_d = self.price_data['High'].transform(lambda x: x.rolling(window=3).max())
        low_k = self.price_data['Low'].transform(lambda x: x.rolling(window=14).min())
        high_k = self.price_data['High'].transform(lambda x: x.rolling(window=14).max())

        stochd = ((self.price_data['Close'] - low_d) / (high_d - low_d)) * 100
        stochk = ((self.price_data['Close'] - low_k) / (high_k - low_k)) * 100
        stochd = stochd.rolling(window=3).mean()
        stochk = stochk.rolling(window=14).mean()
        return stochk, stochd

    def _getMACDData(self):
        """Calculate Moving Average Convergence Divergence Data"""

        sema = self.price_data['Close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
        lema = self.price_data['Close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())
        macd = sema - lema
        sig = macd.transform(lambda x: x.ewm(span=9, adjust=False).mean())
        return macd, sig

    def _getADR(self):
        """Calculate Average Daily Range"""

        l = 7
        last_week = self.price_data.tail(l)
        daily_ranges = np.array([])
        for i in range(l):
            dr = last_week.iloc[i]['High'] - last_week.iloc[i]['Low']
            hc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Close'])
            lc = np.abs(last_week.iloc[i]['High'] - last_week.iloc[i]['Low'])
            m = np.array([dr, hc, lc]).max()
            daily_ranges = np.append(daily_ranges, m)
        adr = np.mean(daily_ranges)
        return adr

    def _getPrice(self):
        """Get current price"""

        return self.price_data['Close'].iloc[-1]

    def _getRSI(self):
        """Get Current RSI"""

        return self.rsi_data[-1]

    def _getStoch(self):
        """Get Current Stoch"""

        return self.stochk_data[-1], self.stochd_data[-1]

    def _getMACD(self):
        """Get Current MACD and MACD Signal"""
        return self.macd_data[-1], self.macd_sig_data[-1]

    def _getStopPrice(self):
        """Get Stop Loss Price"""
        return self.stop

    def _getSellPrice(self):
        """Get Take profit Sell price"""
        return self.sell

    def _profitability(self):
        """
        Determine profitability of a company using income statement, balance sheet, and cash flow
        :return: p_score - total profitability score from 0 to 4
        """

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
        avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]][
            'totalAssets']) / 2
        avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]][
            'totalAssets']) / 2
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

    def _leverage(self):
        """
        Determine leverage of a company with balance sheet
        :return: l_score - total leverage score from 0 to 2
        """

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

    def _operating_efficiency(self):
        """
        Determine operating efficency of a company
        :return: oe_score - score representing operating efficency from 0 to 2
        """

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
        avg_assets = (self.balance_sheet[self.years[0]]['totalAssets'] + self.balance_sheet[self.years[1]][
            'totalAssets']) / 2
        avg_assets_last = (self.balance_sheet[self.years[1]]['totalAssets'] + self.balance_sheet[self.years[2]][
            'totalAssets']) / 2
        at = revenue / avg_assets
        at_last = revenue_last / avg_assets_last
        at_score = 1 if at > at_last else 0
        oe_score += at_score

        return oe_score

    def _get_score(self):
        """
        Returns total score based on profitability, leverage, and operating efficiency
        :return: s - total score from 0 (worst) to 8 (best)
        """

        s = self._profitability() + self._leverage() + self._operating_efficiency()
        return s

    def _get_analysis(self, timestamp='now'):
        '''
        Returns an analysis of given stock in terms of a buy,
        sell, or hold position. Estimated 9% gain
        Return: string 'Buy', 'Sell', or 'Hold'
        '''

        if timestamp == 'now':
            rsi = self.rsi
            stoch = self.stochk
            macd = self.macd > self.macd_sig
            up = self.price > self.avg_50 and self.avg_50 > self.avg_200
        else:
            rsi = self.rsi_data.loc[timestamp]
            stoch = self.stochk_data.loc[timestamp]
            macd = self.macd_data.loc[timestamp] > self.macd_sig_data.loc[timestamp]
            if timestamp in self.avg_200_data.index:
                up = (self.price_data.loc[timestamp] > self.avg_50_data.loc[timestamp]
                      and self.avg_50_data.loc[timestamp] > self.avg_200_data.loc[timestamp])
            else:
                up = True

        if (rsi > 50 and
                stoch > 50 and
                macd and
                up):
            return 'Buy'
        elif (rsi < 50 and
              stoch < 50 and
              macd and
              not up):
            return 'Sell'
        else:
            return 'Hold'
