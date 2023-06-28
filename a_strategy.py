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
    def __init__(self, market_data_manager, portfolio_manager) -> None:
        super().__init__() 
        self.market_data_manager = market_data_manager
        self.portfolio_manager = portfolio_manager 

    def on_order_add(self):
        pass 

    def on_trade_add(self):
        pass

    def add_book_listener(self, symbol):
        self.market_data_manager.get_orderbook(symbol=symbol).add_book_listener(strategy=self)

    def remove_book_listener(self, symbol):
        self.market_data_manager.get_orderbook(symbol=symbol).remove_book_listener(strategy=self) 
    

class SimpleMovingAvgStrategy(BaseStrategy):
    def __init__(self, market_data_manager, portfolio_manager, window_size = 14) -> None:
        super().__init__(market_data_manager, portfolio_manager) 
        self.window_size = window_size
        self.candles = []
        self.sum = 0
    
    def on_order_add(self, message):
        pass

    def on_trade_add(self, new_candle: dict[str, float], message: dict[str, float]):
        self.candles.append(new_candle)
        self.sum += new_candle["price"]
        if len(self.candles) > self.window_size:
            popped = self.candles.pop(0)
            self.sum -= popped["price"]

        assert len(self.candles) == self.window_size
        cur_moving_avg = self.sum / self.window_size
        
        if self.candles[-1]["price"] > cur_moving_avg:
            self.portfolio_manager.sell(message["bidPx"], message["bidSz"]) 
        elif self.candles[-1]["price"] < cur_moving_avg:
            self.portfolio_manager.buy(message["askPx"], message["askSz"])
        else:
            self.portfolio_manager.rebalance(message["askPx"], message["askSz"])

        print("PNL:", self.portfolio_manager.get_pnl(message["last"]))
        
    

class RSIStrategy(BaseStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__(market_data_manager, pnl_tracker)

    def on_order_add(self):
        pass

    def on_trade_add(self):
        pass