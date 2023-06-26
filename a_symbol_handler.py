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
        self.data_handler = WSHandler(symbol, self) if type == "live" else HistHandler(symbol)

        if not isinstance(self.orderbook, IOrderbook) or not isinstance(self.data_handler, IDataHandler):
            raise ValueError
    
    def parse_message(self):
        pass 

    def start(self):
        self.data_handler.start()

    def get_orderbook(self):
        return self.orderbook


class OKXSymbolHandler(BaseSymbolHandler):
    def parse_message(self, message, type):
        print(message)
        self.orderbook.orderbook_add(message, type)
        

    def start(self):
        self.data_handler.start()
