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
    

class SimpleMovingAvgStrategy(BaseStrategy):
    def __init__(self, market_data_manager, pnl_tracker, window_size = 14, candle_length_ms = 100) -> None:
        super().__init__(market_data_manager, pnl_tracker) 
        # self.past_trades = []
        self.generated_candles = [] # list of {closing prices, time}
        self.window_size = window_size
        self.candle_length_ms = candle_length_ms
    
    def on_order_add(self, message):
        pass

    def on_trade_add(self, message: dict[str, float]):
        # self.past_trades.append(message["last"])
        # print("here", self.past_trades)

        if not self.generated_candles or (message["ts"] - self.generated_candles[-1]["ts"] >= self.candle_length_ms):
            self.generated_candles.append({"price": message["last"], "ts": message["ts"]})

        if len(self.generated_candles) > self.window_size:
            assert len(self.generated_candles) == self.window_size + 1
            cur_moving_avg = sum([obj["price"] for obj in self.generated_candles[:-1]])/self.window_size # change this to O(1) update, easy to do
            
            if self.generated_candles[-1]["price"] > cur_moving_avg:
                print("SMA on trade sell")
                self.pnl_tracker.sell(message["bidPx"] * message["bidSz"]) 
            elif self.generated_candles[-1]["price"] < cur_moving_avg:
                print("SMA on trade buy")
                self.pnl_tracker.buy(message["askPx"] * message["askSz"])

            self.generated_candles.pop(0)

            print(self.generated_candles, cur_moving_avg, self.pnl_tracker.get_balance())
        
    

class RSIStrategy(BaseStrategy):
    def __init__(self, market_data_manager, pnl_tracker) -> None:
        super().__init__(market_data_manager, pnl_tracker)

    def on_order_add(self):
        pass

    def on_trade_add(self):
        pass