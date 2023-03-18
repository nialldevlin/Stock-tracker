import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from ai_predict import AIPredict

class AITrader(AIPredict):
    def __init__(self, model_path, ndp, num_trade, bp_margin=1):
        self.client = TradingClient(os.getenv('ALPACA_API_KEY_ID_PAPER'),
                os.getenv('ALPACA_API_SECRET_KEY_PAPER'),
                paper=True)
        self.account = self.client.get_account()
        self.num_trade = num_trade
        self.bp = int(self.account.buying_power)
        self.bp_margin=bp_margin

        super().__init__(model_path, ndp, 'all')
        self.buy = self.getBest(num_trade)
        self.sell = self.getWorst(num_trade)
    
    def trade(self, side='b'):
        if side == 'b':
            scores = self.buy
            side = OrderSide.BUY
        elif side == 's':
            scores = self.sell
            side = OrderSide.SELL
        else:
            raise ValueError("Side must be char b or s")

        ratio = scores.div(scores.min(axis=1).iloc[0])
        ratio = scores.div(scores.sum(axis=1).iloc[0])
        print(self.bp * self.bp_margin)
        amts = ratio * (self.bp * self.bp_margin)

        for stock in scores.columns:
            price = self.getCurrentPrice(stock)
            qty = int(amts[stock].iloc[0] / price)
            market_order_data = MarketOrderRequest(
                    symbol=stock,
                    qty=qty,
                    side=side,
                    time_in_force=TimeInForce.DAY)
            market_order = self.client.submit_order(
                    order_data=market_order_data)
            print(market_order)

    def evalPortfolio(self, scoreThres=10):
        portfolio = self.client.get_all_positions()
        for position in portfolio:
            if qty > 0 and self.predictions[position.symbol] < scoreThres:
                self.client.close_position(position)
            elif qty < 0 and self.predictions[position.symbol] > -1*scoreThres:
                self.client.close_position(position)

