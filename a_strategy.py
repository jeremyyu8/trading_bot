class IStrategy():
    def __init__(self) -> None:
        pass

    def on_order_add(self):
        raise NotImplementedError 

    def on_trade_add(self):
        raise NotImplementedError
    # def on_order_remove(self):
    #     raise NotImplementedError  

    def add_book_listener(self):
        raise NotImplementedError 

    def remove_book_listener(self):
        raise NotImplementedError  

class BaseStrategy(IStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__() 
        self.market_data_manager = market_data_manager
        self.pnl_tracker = pnl_tracker 

    def on_order_add(self):
        pass 

    def on_trade_add(self):
        pass

    def add_book_listener(self, symbol):
        self.market_data_manager.get_orderbook(symbol=symbol).add_book_listener(strategy=self)

    def remove_book_listener(self, symbol):
        self.market_data_manager.get_orderbook(symbol=symbol).remove_book_listener(strategy=self) 
    

class MovingAvgStrategy(BaseStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__(market_data_manager, pnl_tracker) 
        self.past_trades = []
    
    def on_order_add(self, message):
        pass

    def on_trade_add(self, message):
        self.past_trades.append(message["last"])
        print("here", self.past_trades)
    

class RSIStrategy(BaseStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__(market_data_manager, pnl_tracker)

    def on_order_add(self):
        pass

    def on_trade_add(self):
        pass