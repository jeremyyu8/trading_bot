from strategy import IStrategy

class IOrderbook():
    '''
    Interface for an orderbook, has callbacks for strategies listening for trades, new orders, etc.
    '''
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
        self.candle_length_ms = 1000 # length of candles (ms)
        self.stored_length = 10000 # how many candles get stored in memory
        self.candle_start = 0
        self.prices = [0.0]

    def on_order_add(self, message):
        pass 

    #generate candles for strategies based on average price in last period
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
        #if new candle generated, run strategies that use this specific orderbook
        if self.generate_candle(message):
            for book_listener in self.book_listeners:
                book_listener.on_trade_add(self.generated_candles[-1], message)

    def add_book_listener(self, strategy):
        if not isinstance(strategy, IStrategy):
            raise ValueError
        
        self.book_listeners.append(strategy) 

    def remove_book_listener(self, strategy):
        if not isinstance(strategy, IStrategy):
            raise ValueError
        
        self.book_listeners.remove(strategy)  



# function for managing full price level book, not used in current strategies
def merge_incremental_data(full_load, incremental_load):
    '''
    Merges an incremental book into a full book using two pointers
    '''
    full_bids, new_bids = full_load["bids"], incremental_load["bids"]
    full_asks, new_asks = full_load["asks"], incremental_load["asks"]

    i = j = 0
    bids_final = []
    while i < len(full_bids) and j < len(new_bids):
        if full_bids[i][0] > new_bids[j][0]:
            bids_final.append(full_bids[i])
            i += 1 
        elif full_bids[i][0] < new_bids[j][0]:
            bids_final.append(new_bids[j])
            j += 1 
        else:
            if new_bids[j][1] != 0:
                bids_final.append(new_bids[j])
            i += 1
            j += 1
    
    while i < len(full_bids): 
        bids_final.append(full_bids[i])
        i += 1
    while j < len(new_bids): 
        bids_final.append(new_bids[j])
        j += 1


    i = j = 0
    asks_final = []
    while i < len(full_asks) and j < len(new_asks):
        if full_asks[i][0] < new_asks[j][0]:
            asks_final.append(full_asks[i])
            i += 1 
        elif full_asks[i][0] > new_asks[j][0]:
            asks_final.append(new_asks[j])
            j += 1 
        else:
            if new_asks[j][1] != 0:
                bids_final.append(new_asks[j])
            i += 1
            j += 1
    
    while i < len(full_asks): 
        asks_final.append(full_asks[i])
        i += 1
    while j < len(new_asks): 
        asks_final.append(new_asks[j])
        j += 1

    return {"bids": bids_final, "asks": asks_final}