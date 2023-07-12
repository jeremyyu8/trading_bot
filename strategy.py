import pandas as pd
import numpy as np
class IStrategy():
    '''
    Interface for an automated trading strategy.
    '''
    def __init__(self) -> None:
        pass

    def on_trade_add(self):
        raise NotImplementedError

    def add_book_listener(self):
        raise NotImplementedError 

    def remove_book_listener(self):
        raise NotImplementedError  

class BaseStrategy(IStrategy):
    def __init__(self, market_data_manager, portfolio_manager) -> None:
        super().__init__() 
        self.market_data_manager = market_data_manager
        self.portfolio_manager = portfolio_manager 

    # for each strategy every time new candle is received, generate new signal, then send buy or sell to portfolio manager
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

    def on_trade_add(self, new_candle: dict[str, float], message: dict[str, float]):
        #preprocess new candle
        self.candles.append(new_candle)
        self.sum += new_candle["price"]
        if len(self.candles) > self.window_size:
            popped = self.candles.pop(0)
            self.sum -= popped["price"]

        if len(self.candles) != self.window_size:
            return

        #generate signal
        cur_moving_avg = self.sum / self.window_size
        
        #do action based on signal
        if self.candles[-1]["price"] > cur_moving_avg:
            self.portfolio_manager.sell(message["bidPx"], message["bidSz"], message["symbol"]) 
        elif self.candles[-1]["price"] < cur_moving_avg:
            self.portfolio_manager.buy(message["askPx"], message["askSz"], message["symbol"])
        else:
            self.portfolio_manager.rebalance(message["askPx"], message["askSz"], message["symbol"])
        print("PNL:", self.portfolio_manager.get_pnl())
        
    

class RSIStrategy(BaseStrategy):
    def __init__(self, market_data_manager, portfolio_manager, window_size = 14, buy_thresh = 30, sell_thresh = 70) -> None:
        super().__init__(market_data_manager, portfolio_manager) 
        self.window_size = window_size
        self.last_price = 0
        self.deltas = []
        self.ups = 0
        self.downs = 0
        self.buy_thresh = buy_thresh
        self.sell_thresh = sell_thresh

    def on_trade_add(self, new_candle: dict[str, float], message: dict[str, float]):
        #preprocess new candle
        if self.last_price == 0:
            self.last_price = new_candle["price"] 
            return
        
        diff = new_candle["price"] - self.last_price
        self.deltas.append(diff)
        if diff > 0:
            self.ups += diff 
        else:
            self.downs += abs(diff)

        if len(self.deltas) > self.window_size:
            popped = self.deltas.pop(0)
            if popped > 0:
                self.ups -= popped 
            else:
                self.downs -= abs(popped)

        self.last_price = new_candle["price"]

        if len(self.deltas) != self.window_size:
            return
        
        #generate signal
        avg_ups = self.ups/self.window_size
        avg_downs = self.downs/self.window_size
        if (avg_downs) == 0:
            avg_downs = 0.1
        relative_strength = avg_ups/avg_downs
        rsi = 100 - 100 / (1+relative_strength)
        
        #do action based on signal
        if rsi >= self.sell_thresh:
            self.portfolio_manager.sell(message["bidPx"], message["bidSz"], message["symbol"]) 
        elif rsi <= self.buy_thresh:
            self.portfolio_manager.buy(message["askPx"], message["askSz"], message["symbol"])
        else:
            self.portfolio_manager.rebalance(message["askPx"], message["askSz"], message["symbol"])
        print("PNL:", self.portfolio_manager.get_pnl())

class MACDStrategy(BaseStrategy):
    def __init__(self, market_data_manager, portfolio_manager, short_window = 12, long_window = 26, signal_span = 9, hurst_thresh = 0.6, hurst_len = 100) -> None:
        super().__init__(market_data_manager, portfolio_manager) 
        self.candles = []
        self.historic_prices = []
        self.short_window = short_window
        self.long_window = long_window
        self.signal_span = signal_span
        self.hurst_thresh = hurst_thresh
        self.hurst_len = hurst_len

    def on_trade_add(self, new_candle: dict[str, float], message: dict[str, float]):
        #preprocess new candle
        self.candles.append(new_candle["price"])
        self.historic_prices.append(new_candle["price"])
        if len(self.candles) > self.long_window:
            self.candles.pop(0)
        if len(self.historic_prices) > self.hurst_len:
            self.historic_prices.pop(0)

        if len(self.candles) != self.long_window:
            return

        #generate signal
        data = pd.DataFrame(self.candles, columns=['price'])
        ema_short = data['price'].ewm(span=self.short_window).mean()
        ema_long = data['price'].ewm(span=self.long_window).mean()
        macd = ema_short - ema_long
        macd_signal_line = macd.ewm(span=self.signal_span).mean()
        macd = macd.iloc[-1]
        macd_signal_line = macd_signal_line.iloc[-1]

        #hurst exponent
        hurst = self.get_hurst_exponent(self.historic_prices)


        #do action based on signal, if hurst > 0.5, place order
        if macd > macd_signal_line and hurst > self.hurst_thresh:
                self.portfolio_manager.buy(message["askPx"], message["askSz"], message["symbol"])
        elif macd < macd_signal_line and hurst > self.hurst_thresh:
                self.portfolio_manager.sell(message["bidPx"], message["bidSz"], message["symbol"]) 
        else:
            self.portfolio_manager.rebalance(message["askPx"], message["askSz"], message["symbol"])
        
        
        print("PNL:", self.portfolio_manager.get_pnl())

    def get_hurst_exponent(self, time_series, max_lag=20):
        lags = range(2, max_lag)

        # variances of the lagged differences
        tau = [np.std(np.subtract(time_series[lag:], time_series[:-lag])) for lag in lags]

        # calculate the slope of the log plot -> the Hurst Exponent
        reg = np.polyfit(np.log(lags), np.log(tau), 1)

        return reg[0]