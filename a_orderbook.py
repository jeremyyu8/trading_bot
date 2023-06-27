from a_strategy import IStrategy

class IOrderbook():
    def __init__(self) -> None:
        pass

    def on_order_add(self):
        raise NotImplementedError
    
    def on_trade(self):
        raise NotImplementedError 

    # def onOrderRemove(self):
    #     raise NotImplementedError 

    # def onTradeCancel(self):
    #     raise NotImplementedError



class PriceLevelBook(IOrderbook):
    def __init__(self) -> None:
        super().__init__()
        self.book_listeners = []
        self.generated_candles = [] # list of {closing prices, time}
        self.candle_length_ms = 1000 # add to input
        self.stored_length = 10000 # add to input
        self.candle_start = 0
        self.prices = [0.0]

    def on_order_add(self, message):
        pass 

    def generate_candle(self, message):
        if message["ts"] > self.candle_start+self.candle_length_ms:
            self.generated_candles.append({"price": sum(self.prices)/len(self.prices)})
            if len(self.generated_candles) > self.stored_length:
                self.generated_candles.pop(0)
            self.candle_start = message["ts"]//self.candle_length_ms * self.candle_length_ms
            self.prices = [message["last"]]
            return True
        else:
            self.prices.append(message["last"])
            return False
        

    def on_trade(self, message):
        if self.generate_candle(message):
            for book_listener in self.book_listeners:
                book_listener.on_trade_add(self.generated_candles[-1], message)

    def add_book_listener(self, strategy):
        if not isinstance(strategy, IStrategy):
            raise ValueError
        
        self.book_listeners.append(strategy) 

    def remove_book_listener(self, strategy):
        pass 