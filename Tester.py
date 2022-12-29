from trader import Trader, Side

t = Trader(live=False)
t.tradePositions(side=Side.SELL)