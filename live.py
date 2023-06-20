import requests
import pandas as pd

from main import make_okx_api_call


class LiveTrader:
    def __init__(self, symbol):
        self.symbol = symbol
        self.data = None
        self.price = None
        self.shares = 0

    ########################################## FETCH DATA ##########################################

    def get_spot_price(self):
        '''
        Get the spot price for a given symbol, returns the price as a float
        '''

        params = {'instId': self.symbol}
        response = make_okx_api_call('/api/v5/market/ticker', params)
        spot_price = float(response['data'][0]['last'])
        self.price = spot_price
        print(self.price)

    ########################################## STRATEGIES ##########################################

    def basic_moving_average_strategy(symbol, threshold=0.05):
        '''
        Returns "Buy", "Sell", or "None"
        '''
        pass

    def position_sizing(self):
        pass

    def stop_loss(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

    def simulate_strategy_live(symbol, strategy, initial_balance, freq):
        pass


live_trader = LiveTrader('BTC-USDT')
for i in range(30):
    live_trader.get_spot_price()
