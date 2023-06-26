import json 
import websocket
import typing

BaseSymbolHandler = typing.TypeVar('BaseSymbolHandler')


class IDataHandler():
    def __init__(self) -> None:
        pass
    
    def on_message(self):
        raise NotImplementedError 
    
    def start(self):
        raise NotImplementedError

class WSHandler(IDataHandler):
    def __init__(self, url: str, subscription_args: list[dict], symbol: str, symbol_handler: BaseSymbolHandler) -> None:
        super().__init__()
        self.symbol = symbol
        self.symbol_handler = symbol_handler
        self.url = url
        self.subscription_args = subscription_args
    
    def on_message(self, ws, message):
        self.symbol_handler.parse_message(json.loads(message), "live")

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

        #x = threading.Thread(target=symbol_handler.start(), daemon = True)
        self.ws.run_forever()

    
    

class HistHandler(IDataHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def on_message(self):
        pass 

    def start(self):
        pass
    
    