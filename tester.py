#!../stracker/bin/python3

from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta

ticker = 'WMT'

handler = TA_Handler(
    symbol=ticker,
    exchange="NYSE",
    screener="america",
    interval=Interval.INTERVAL_1_DAY
)

analysis = handler.get_analysis()

oscillators = analysis.oscillators
indicators = analysis.indicators
summary = analysis.summary

rsi = indicators['RSI']
stochk = indicators['Stoch.K']
stochd = indicators['Stoch.D']
macd = indicators['MACD.macd']
sig = indicators['MACD.signal']

if rsi > 50 and stochk > 50 and stochd > 50 and macd > sig:
	powerXAnalysis = 'Buy'
elif rsi < 50 and stochk < 50 and stochd < 50 and macd < sig:
	powerXAnalysis = 'Sell'
else:
	powerXAnalysis = 'Hold'
