from typing import *
import pandas as pd
import matplotlib.pyplot as plt

import websocket
import json
import time



class OrderBook:
    def __init__(self, trading_pair):
        self.trading_pair = trading_pair
        self.ws = None
        self.order_book = None
        self.most_recent_time = None 
        self.is_running = False

    def on_message(self, ws, message):
        # Parse the message as JSON
        data = json.loads(message)
        # print("message received")
        self.process_order_book(data)

    def on_error(self, ws, error):
        print("error:", error)

    def on_close(self, ws):
        print("Connection closed")
        self.is_running = False

    def on_open(self, ws):
        subscribe_message = {
            "op": "subscribe",
            "args": [{"channel": "books",
                      "instId": "BTC-USDT"
                      }]
        }
        ws.send(json.dumps(subscribe_message))

    def connect(self):
        self.is_running = True
        self.ws = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public",
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever()
    
    def process_order_book(self, data):
        bids, asks, ts = data['data'][0]['bids'], data['data'][0]['asks'], data['data'][0]['ts']
        self.most_recent_time = ts 

        '''
            will change which data is held
            An example of the array of asks and bids values: ["411.8", "10", "0", "4"]
            - "411.8" is the depth price
            - "10" is the quantity at the price (number of contracts for derivatives, quantity in base currency for Spot and Spot Margin)
            - "0" is part of a deprecated feature and it is always "0"
            - "4" is the number of orders at the price.
            '''
        
        new_book = {"bids": [(float(bid[0]), float(bid[3])) for bid in bids], "asks": [(float(ask[0]), float(ask[3])) for ask in asks]}
        

        if data['action'] == "snapshot":
            self.order_book = new_book
        elif data['action'] == "update":
            self.order_book = merge_incremental_data(self.order_book, new_book)
        
        print()
        print(self.order_book)

    def get_bids(self):
        return self.order_book["bids"]
    
    def get_asks(self):
        return self.order_book["asks"]
    
    def get_time(self):
        return self.most_recent_time
    
    def visualize(self):
        bid_prices, bid_quantities = zip(*self.get_bids())
        ask_prices, ask_quantities = zip(*self.get_asks())

        mean_spread = (bid_prices[0] + ask_prices[0]) / 2

        fig, ax = plt.subplots()
        ax.bar(bid_prices, bid_quantities, align='edge', width=-0.4, color='g', label='Bids')
        ax.bar(ask_prices, ask_quantities, align='edge', width=0.4, color='r', label='Asks')
        ax.axvline(x=mean_spread, color='b', linestyle='--', label='Mean Spread')
        
        ax.set_xlabel('Price')
        ax.set_ylabel('Quantity')
        ax.set_title(f'Order Book - : {self.symbol}')

        ax.legend()

        plt.tight_layout()
        plt.show()

def merge_incremental_data(full_load, incremental_load):
    '''
    Merges an incremental book into a full book using two pointers
    '''
    full_bids, new_bids = full_load["bids"], incremental_load["bids"]
    full_asks, new_asks = full_load["asks"], incremental_load["asks"]

    i = j = 0
    bids_final = []
    while i < len(full_bids) and j < len(new_bids):
        if full_bids[i][0] > new_bids[j][0]:
            bids_final.append(full_bids[i])
            i += 1 
        elif full_bids[i][0] < new_bids[j][0]:
            bids_final.append(new_bids[j])
            j += 1 
        else:
            if new_bids[j][1] != 0:
                bids_final.append(new_bids[j])
            i += 1
            j += 1
    
    while i < len(full_bids): 
        bids_final.append(full_bids[i])
        i += 1
    while j < len(new_bids): 
        bids_final.append(new_bids[j])
        j += 1


    i = j = 0
    asks_final = []
    while i < len(full_asks) and j < len(new_asks):
        if full_asks[i][0] < new_asks[j][0]:
            asks_final.append(full_asks[i])
            i += 1 
        elif full_asks[i][0] > new_asks[j][0]:
            asks_final.append(new_asks[j])
            j += 1 
        else:
            if new_asks[j][1] != 0:
                bids_final.append(new_asks[j])
            i += 1
            j += 1
    
    while i < len(full_asks): 
        asks_final.append(full_asks[i])
        i += 1
    while j < len(new_asks): 
        asks_final.append(new_asks[j])
        j += 1

    return {"bids": bids_final, "asks": asks_final}

# Create an instance of the OrderBook class and connect
order_book = OrderBook("BTC-USDT")
order_book.connect()