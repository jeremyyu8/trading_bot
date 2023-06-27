from a_orderbook import IOrderbook, PriceLevelBook
from a_data_handler import IDataHandler, WSHandler, HistHandler

class ISymbolHandler():
    def __init__(self) -> None:
        pass
    
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


class OKXSymbolHandler(BaseSymbolHandler):
    def __init__(self, symbol, type) -> None:
        super().__init__(symbol, type)

        if type == "live":
            self.data_handler = WSHandler(
            url="wss://ws.okx.com:8443/ws/v5/public", 
            subscription_args=[{"channel": "tickers", "instId": symbol}], 
            symbol=symbol, 
            symbol_handler=self)
        else:
            self.data_handler = HistHandler(symbol)

        if not isinstance(self.data_handler, IDataHandler):
            raise ValueError

    def parse_message(self, message: dict[str, list[dict]], type: str):
        if type == "live":
            data = message["data"][0]
            #print(data)
            self.orderbook.on_trade({"last": float(data["last"]), 
                                 "lastSz": float(data["lastSz"]),
                                 "ts": float(data["ts"]),
                                 "askPx": float(data["askPx"]), 
                                 "askSz": float(data["askSz"]), 
                                 "bidPx": float(data["bidPx"]), 
                                 "bidSz": float(data["bidSz"])}) 
            
        else:
            pass
        

    def start(self):
        self.data_handler.start()

'''
h":"30827","high24h":"30886.6","low24h":"29962","sodUtc0":"30467.6","sodUtc8":"30588.2","volCcy24h":"226848774.714833958","vol24h":"7455.88473797","ts":"1687762124712"}]}
{"arg":{"channel":"tickers","instId":"BTC-USDT"},"data":[{"instType":"SPOT","instId":"BTC-USDT","last":"30301.5","lastSz":"0.0013","askPx":"30300.3","askSz":"2.68385152","bidPx":"30300.2","bidSz":"0.67476737","open24h":"30827","high24h":"30886.6","low24h":"29962","sodUtc0":"30467.6","sodUtc8":"30588.2","volCcy24h":"226848774.714833958","vol24h":"7455.88473797","ts":"1687762124866"}]}
{"arg":{"channel":"tickers","instId":"BTC-USDT
'''
