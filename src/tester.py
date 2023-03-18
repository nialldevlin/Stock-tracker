from ai_trader import AITrader

t = AITrader('../data/model.h5', 70, 5)
t.evalPortfolio()
t.trade('s')
