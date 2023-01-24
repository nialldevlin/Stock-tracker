from trader import Trader, Side

t = Trader()
rec = t.getBuySellReccomendation()
t.tradePositions(margin=1.0, side=rec)