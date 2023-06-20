import requests
import pandas as pd
import json
import websocket
import threading
import time

from main import make_okx_api_call


class LiveTrader:
    def __init__(self, symbol):
        # websocket info
        self.symbol = symbol
        self.is_running = False
        self.ws1 = None
        self.ws2 = None
        self.ws3 = None

        # trading status
        self.shares = 0

        # ticker prices
        self.price = None
        self.ask_price = None
        self.bid_price = None
        self.ask_size = None
        self.bid_size = None

        self.trade_id = None
        self.trade_price = None
        self.trade_side = None

    ########################################## FETCH DATA ##########################################

    def on_message_ticker(self, ws, message):
        response = json.loads(message)
        # print(response)

        self.price = float(response['data'][0]['last'])
        self.ask_price = float(response['data'][0]['askPx'])
        self.bid_price = float(response['data'][0]['bidPx'])
        self.ask_size = float(response['data'][0]['askSz'])
        self.bid_size = float(response['data'][0]['bidSz'])
        print(self.price)

    def on_message_trade(self, ws, message):
        response = json.loads(message)
        # print(response)

        self.tradeId = int(response['data'][0]['tradeId'])
        self.trade_price = float(response['data'][0]['px'])
        self.side = str(response['data'][0]['side'])
        print(self.tradeId, self.price, self.side)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws):
        print("Connection closed")
        self.is_running = False

    def on_open_ticker(self, ws):
        subscribe_message = {
            "op": "subscribe",
            "args": [{
                "channel": "tickers",
                "instId": self.symbol
            }]
        }
        ws.send(json.dumps(subscribe_message))

    def on_open_trade(self, ws):
        subscribe_message = {
            "op": "subscribe",
            "args": [{
                "channel": "trades",
                "instId": self.symbol
            }]
        }
        ws.send(json.dumps(subscribe_message))

    def connect(self):
        self.ws1 = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public",
                                          on_message=self.on_message_ticker,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws1.on_open = self.on_open_ticker

        self.ws2 = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public",
                                          on_message=self.on_message_trade,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws2.on_open = self.on_open_trade

        wst1 = threading.Thread(target=self.ws1.run_forever, daemon=True)
        wst1.start()
        wst2 = threading.Thread(target=self.ws2.run_forever, daemon=True)
        wst2.start()

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


live_trader = LiveTrader('BTC-USD-SWAP')
live_trader.connect()
time.sleep(100)
# for i in range(30):
#     live_trader.get_spot_price()
