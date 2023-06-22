class IStrategy():
    def __init__(self) -> None:
        pass

    def on_orderbook_listener_add(self):
        raise NotImplementedError 

    def on_orderbook_listener_remove(self):
        raise NotImplementedError  

    def add_book_listener(self):
        raise NotImplementedError 

    def remove_book_listener(self):
        raise NotImplementedError  

class MovingAvgStrategy(IStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__() 
        self.market_data_manager = market_data_manager
        self.pnl_tracker = pnl_tracker 

        self.add_book_listener(self.market_data_manager.get_orderbook())
    
    def on_orderbook_listener_add(self):
        pass

    def on_orderbook_listener_remove(self):
        pass

    def add_book_listener(self, orderbook):
        orderbook.add_book_listener(self)

    def remove_book_listener(self):
        pass
    

class RSIStrategy(IStrategy):
    pass