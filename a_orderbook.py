from a_strategy import IStrategy

class IOrderbook():
    def __init__(self) -> None:
        pass

    def on_order_add(self):
        raise NotImplementedError

    # def onOrderRemove(self):
    #     raise NotImplementedError 

    # def onTrade(self):
    #     raise NotImplementedError 

    # def onTradeCancel(self):
    #     raise NotImplementedError



class PriceLevelBook(IOrderbook):
    def __init__(self) -> None:
        super().__init__()
        self.book_listeners = []

    def on_order_add(self):
        pass 

    def add_book_listener(self, strategy):
        if not isinstance(strategy, IStrategy):
            raise ValueError
        
        self.book_listeners.append(strategy) 

    def remove_book_listener(self, strategy):
        pass 