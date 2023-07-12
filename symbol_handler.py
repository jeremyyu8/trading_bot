from orderbook import IOrderbook, PriceLevelBook
from data_handler import IDataHandler, WSHandler, HistHandler
import csv
from datetime import datetime
import time

class ISymbolHandler():
    '''
    Interface for handling one individual symbol on an exchange
    '''

    #for each symbol handler, there is unique initialization for live, historic, and download
    def __init__(self) -> None:
        pass
    
    #for each symbol handler, there is unique message that needs to be parsed for live, historic, and download
    def parse_message(self):
        raise NotImplementedError 
    
    def start(self):
        raise NotImplementedError
    
    def get_orderbook(self):
        raise NotImplementedError


class BaseSymbolHandler(ISymbolHandler):
    def __init__(self, symbol, type) -> None:
        super().__init__()
        self.orderbook = PriceLevelBook() 

        if not isinstance(self.orderbook, IOrderbook):
            raise ValueError
    
    def parse_message(self):
        pass 

    def start(self):
        self.data_handler.start()

    def get_orderbook(self):
        return self.orderbook

class BinanceSymbolHandler(BaseSymbolHandler):
    def __init__(self, symbol, type) -> None:
        super().__init__(symbol, type)
        self.symbol = symbol

        if type == "live":
            self.data_handler = WSHandler(
                url="wss://stream.binance.us:9443/ws", 
                subscribe_message = {"method": "SUBSCRIBE",
                                    "params": [f"{symbol.lower()}@ticker"],
                                    "id": int(time.time())}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
            
        elif type == "historic":
            self.data_handler = HistHandler(
                symbol = symbol,
                symbol_handler=self)
            
        elif type == "download":
            #initialize csv file
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'w') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                csvwriter.writerow(["last", "lastSz", "ts", "askPx", "askSz", "bidPx", "bidSz"]) 
                csvfile.close()

            #start websocket to collect data
            self.data_handler = WSHandler(
                url="wss://stream.binance.us:9443/ws", 
                subscribe_message = {"method": "SUBSCRIBE",
                                    "params": [f"{symbol.lower()}@ticker"],
                                    "id": int(time.time())}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
        else:
            print("Invalid data type.")

        if not isinstance(self.data_handler, IDataHandler):
            raise ValueError
        
    
    def parse_message(self, message, type):
        if type == "live":
            data = message
            self.orderbook.on_trade({"last": float(data["c"]), 
                                 "lastSz": float(data["Q"]),
                                 "ts": float(data["E"]),
                                 "askPx": float(data["a"]), 
                                 "askSz": float(data["A"]), 
                                 "bidPx": float(data["b"]), 
                                 "bidSz": float(data["B"]),
                                 "symbol": self.symbol}) 
            
        elif type == "historic":
            data = message
            self.orderbook.on_trade({"last": float(data["last"]), 
                                 "lastSz": float(data["lastSz"]),
                                 "ts": float(data["ts"]),
                                 "askPx": float(data["askPx"]), 
                                 "askSz": float(data["askSz"]), 
                                 "bidPx": float(data["bidPx"]), 
                                 "bidSz": float(data["bidSz"]),
                                 "symbol": self.symbol})      
        elif type == "download":
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'a') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                data = message
                fields = [data["c"], data["Q"], data["E"], data["a"], data["A"], data["b"], data["B"]]
                csvwriter.writerow(fields) 
                csvfile.close() 


class CoinbaseSymbolHandler(BaseSymbolHandler):
    def __init__(self, symbol, type) -> None:
        super().__init__(symbol, type)
        self.symbol = symbol 

        if type == "live":
            self.data_handler = WSHandler(
                url="wss://ws-feed.exchange.coinbase.com/ws", 
                subscribe_message = {"type": "subscribe",
                                    "product_ids": [symbol],
                                    "channels": ["ticker"]}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
            
        elif type == "historic":
            self.data_handler = HistHandler(
                symbol = symbol,
                symbol_handler=self)
            
        elif type == "download":
            #initialize csv file
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'w') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                csvwriter.writerow(["last", "lastSz", "ts", "askPx", "askSz", "bidPx", "bidSz"]) 
                csvfile.close()

            #start websocket to collect data
            self.data_handler = WSHandler(
                url="wss://ws-feed.exchange.coinbase.com/ws", 
                subscribe_message = {"type": "subscribe",
                                    "product_ids": [symbol],
                                    "channels": ["ticker"]}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
        else:
            print("Invalid data type.")

        if not isinstance(self.data_handler, IDataHandler):
            raise ValueError
        
    
    def parse_message(self, message, type):
        if type == "live":
            data = message
            #print(data)
            ms = int(datetime.fromisoformat(data["time"]).timestamp() * 1000)
            self.orderbook.on_trade({"last": float(data["price"]), 
                                 "lastSz": float(data["last_size"]),
                                 "ts": ms,
                                 "askPx": float(data["best_ask"]), 
                                 "askSz": float(data["best_ask_size"]), 
                                 "bidPx": float(data["best_bid"]), 
                                 "bidSz": float(data["best_bid_size"]),
                                 "symbol": self.symbol}) 
            
        elif type == "historic":
            data = message
            self.orderbook.on_trade({"last": float(data["last"]), 
                                 "lastSz": float(data["lastSz"]),
                                 "ts": float(data["ts"]),
                                 "askPx": float(data["askPx"]), 
                                 "askSz": float(data["askSz"]), 
                                 "bidPx": float(data["bidPx"]), 
                                 "bidSz": float(data["bidSz"]),
                                 "symbol": self.symbol})      
        elif type == "download":
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'a') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                data = message
                ms = int(datetime.fromisoformat(data["time"]).timestamp() * 1000)

                fields = [data["price"], data["last_size"], ms , data["best_ask"], data["best_ask_size"], data["best_bid"], data["best_bid_size"]]
                csvwriter.writerow(fields) 
                csvfile.close() 

class OKXSymbolHandler(BaseSymbolHandler):
    def __init__(self, symbol, type) -> None:
        super().__init__(symbol, type)
        self.symbol = symbol

        if type == "live":
            self.data_handler = WSHandler(
                url="wss://ws.okx.com:8443/ws/v5/public", 
                subscribe_message = {"op": "subscribe",
                                    "args": [{"channel": "tickers", "instId": symbol}]}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
            
        elif type == "historic":
            self.data_handler = HistHandler(
                symbol = symbol,
                symbol_handler=self)
            
        elif type == "download":
            #initialize csv file
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'w') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                csvwriter.writerow(["last", "lastSz", "ts", "askPx", "askSz", "bidPx", "bidSz"]) 
                csvfile.close()

            #start websocket to collect data
            self.data_handler = WSHandler(
                url="wss://ws.okx.com:8443/ws/v5/public", 
                subscribe_message = {"op": "subscribe",
                                    "args": [{"channel": "tickers", "instId": symbol}]}, 
                symbol=symbol, 
                symbol_handler=self,
                data_action=type)
        else:
            print("Invalid data type.")

        if not isinstance(self.data_handler, IDataHandler):
            raise ValueError



    def parse_message(self, message: dict[str, list[dict]], type: str):
        if type == "live":
            data = message["data"][0]
            self.orderbook.on_trade({"last": float(data["last"]), 
                                 "lastSz": float(data["lastSz"]),
                                 "ts": float(data["ts"]),
                                 "askPx": float(data["askPx"]), 
                                 "askSz": float(data["askSz"]), 
                                 "bidPx": float(data["bidPx"]), 
                                 "bidSz": float(data["bidSz"]),
                                 "symbol": self.symbol}) 
            
        elif type == "historic":
            data = message
            self.orderbook.on_trade({"last": float(data["last"]), 
                                 "lastSz": float(data["lastSz"]),
                                 "ts": float(data["ts"]),
                                 "askPx": float(data["askPx"]), 
                                 "askSz": float(data["askSz"]), 
                                 "bidPx": float(data["bidPx"]), 
                                 "bidSz": float(data["bidSz"]),
                                 "symbol": self.symbol}) 
            
            
        elif type == "download":
            filename = 'historical_data/' + self.symbol + '_data.csv'
            with open(filename, 'a') as csvfile: 
                # creating a csv writer object 
                csvwriter = csv.writer(csvfile) 
                # writing the fields 
                data = message["data"][0]
                fields = [data["last"], data["lastSz"], data["ts"], data["askPx"], data["askSz"], data["bidPx"], data["bidSz"]]
                csvwriter.writerow(fields) 
                csvfile.close()

