import json 
import websocket
import typing
import pandas as pd

BaseSymbolHandler = typing.TypeVar('BaseSymbolHandler')


class IDataHandler():
    def __init__(self) -> None:
        pass
    
    def on_message(self):
        raise NotImplementedError 
    
    def start(self):
        raise NotImplementedError

class WSHandler(IDataHandler):
    def __init__(self, url: str, subscription_args: list[dict], symbol: str, symbol_handler: BaseSymbolHandler, data_action: str) -> None:
        super().__init__()
        self.symbol = symbol
        self.symbol_handler = symbol_handler
        self.url = url
        self.subscription_args = subscription_args
        self.data_action = data_action
    
    def on_message(self, ws, message):
        if self.data_action == "live":
            self.symbol_handler.parse_message(json.loads(message), self.data_action)
        elif self.data_action == "download":
            self.symbol_handler.parse_message(json.loads(message), self.data_action)

    def on_error(self, ws, error):
        print("error:", error)
    
    def on_close(self, ws):
        print("Connection closed")
    
    def on_open(self, ws):
        subscribe_message = {
            "op": "subscribe",
            "args": self.subscription_args
        }
        ws.send(json.dumps(subscribe_message))

    def start(self):
        self.ws = websocket.WebSocketApp( url = self.url,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever()

    

class HistHandler(IDataHandler):
    def __init__(self, symbol: str, symbol_handler: BaseSymbolHandler) -> None:
        super().__init__()
        self.symbol = symbol
        self.symbol_handler = symbol_handler
        self.file_name = symbol + "_data.csv"
        self.data = pd.read_csv(self.file_name)
    
    def on_message(self, message):
        self.symbol_handler.parse_message(message, "historic")

    def start(self):
        for index, row in self.data.iterrows():
            self.symbol_handler.parse_message(row, "historic")
            
            

    
    