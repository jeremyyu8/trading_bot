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

    def on_order_add(self, message):
        pass 

    def on_trade(self, message):
        for book_listener in self.book_listeners:
            book_listener.on_trade_add(message)

    def add_book_listener(self, strategy):
        if not isinstance(strategy, IStrategy):
            raise ValueError
        
        self.book_listeners.append(strategy) 

    def remove_book_listener(self, strategy):
        pass 