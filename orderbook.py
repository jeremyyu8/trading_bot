import pandas as pd
import matplotlib.pyplot as plt

from main import make_okx_api_call


class OrderBook:
    '''
    Class for storing and updating orderbooks for individual symbols
    '''
    def __init__(self, symbol):
        self.symbol = symbol 
        self.order_book = None 
    
    def fetch(self, size):
        params = {"instId": self.symbol, "sz": str(size)}
        request = make_okx_api_call('/api/v5/market/books', params=params)
        print(request['data'][0])
        bids = request['data'][0]['bids']
        asks = request['data'][0]['asks']
        
        # weird way data is given, theres quantity at the price in base currency and number of orders??
        data = {"bidQty": [float(bid[3]) for bid in bids], "bidPx": [float(bid[0]) for bid in bids], "askPx": [float(ask[0]) for ask in asks], "askQty": [float(ask[3]) for ask in asks]}
        self.order_book = pd.DataFrame(data)

    def get_bids(self):
        return self.order_book[['bidPx', 'bidQty']]
    
    def get_asks(self):
        return self.order_book[['askPx', 'askQty']]
    
    def get_book(self):
        return self.order_book

    def get_date(self):
        '''
        Returns time in ms
        '''
        return self.order_book.ts

    def visualize(self):

        bid_prices, bid_quantities = self.order_book['bidPx'].tolist(), self.order_book['bidQty'].tolist()
        ask_prices, ask_quantities = self.order_book['askPx'].tolist(), self.order_book['askQty'].tolist()

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


class OrderBookHolder:
    '''
    Class for storing and updating multiple orderbooks
    '''

    def __init__(self, symbols):
        self.symbols = symbols 
        self.order_books = {symbol: OrderBook(symbol) for symbol in symbols} 

    def get_symbols(self):
        return self.symbols 
    
    def fetch_all(self, size):
        for symbol in self.order_books:
            self.order_books[symbol].fetch(size)
    
    def __getitem__(self, symbol):
        return self.order_books[symbol]


orderbook = OrderBook('BTC-USDT')
orderbook.fetch(8)
print(orderbook.get_book())
orderbook.visualize()

many_books = OrderBookHolder(['BTC-USDT', 'WIFI-USDT', 'XRP-BTC'])
many_books.fetch_all(5)
print(many_books['XRP-BTC'].get_book())