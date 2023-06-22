import json 
import websocket
from typing import NewType

from a_symbol_handler import BaseSymbolHandler, OKXSymbolHandler



class IDataHandler():
    def __init__(self) -> None:
        pass
    
    def on_message(self):
        raise NotImplementedError 
    
    def start(self):
        raise NotImplementedError

class WSHandler(IDataHandler):
    def __init__(self, symbol: str, symbol_handler: OKXSymbolHandler) -> None:
        super().__init__()
        self.symbol = symbol
        self.symbol_handler = symbol_handler
    
    def on_message(self, ws, message):
        self.symbol_handler.parse_message(message, "live")

    def on_error(self, ws, error):
        print("error:", error)
    
    def on_close(self, ws):
        print("Connection closed")
    
    def on_open(self, ws):
        subscribe_message = {
            "op": "subscribe",
            "args": [{"channel": "books",
                      "instId": self.symbol
                      }]
        }
        ws.send(json.dumps(subscribe_message))

    def start(self):
        self.ws = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public",
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever()

    
    

class HistHandler(IDataHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def on_message(self):
        pass 

    def start(self):
        pass
    
    