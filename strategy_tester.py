from stock_analyzer import  Stockalyzer

def runSimulation(ticker, starting_cash, verbose=False):
    sa = Stockalyzer(ticker)
    balance = starting_cash
    stocks = 0
    #b_or_s = True # False last bought, True last sold
    for i in sa.price_data.index:
        price = sa.price_data['open'].loc[i]
        if sa.getAnalysis(i) == 'Buy':
            buy_amount = int(balance / price)
            balance -= buy_amount * price
            stocks += buy_amount
            if buy_amount > 0 and verbose:
                print('Bought {} of {} at {}'.format(buy_amount, ticker, price))
        else:
            balance += stocks * price
            if stocks > 0 and verbose:
                print('Sold {} of {} at {}'.format(stocks, ticker, price))
            stocks = 0
    return balance + stocks * sa.price

