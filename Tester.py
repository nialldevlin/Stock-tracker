from trader import Trader, Side

t = Trader()
rec = t.getBuySellReccomendation()
t.tradePositions(side=rec)