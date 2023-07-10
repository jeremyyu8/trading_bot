import threading
class PortfolioManager():
    '''
    Manages risk among all strategies, tracks positions and PNL over all strategies and exchanges
    '''

    def __init__(self, initial_balance, risk_manager, equities) -> None:
        self.long = {key: value for key, value in zip(equities, [0 for i in range(len(equities))])}
        self.short = {key: value for key, value in zip(equities, [0 for i in range(len(equities))])}
        self.prices = {key: value for key, value in zip(equities, [0 for i in range(len(equities))])}
        self.initial_balance = initial_balance
        self.balance = initial_balance 
        self.risk_manager = risk_manager
        self.convex_risk_manager_equity = 0
        self.pnls = []
        self.portfolio_lock = threading.Lock()

    #Constant Proportion Portfolio Insurance (CPPI)
    def cppi_risk_manager(self, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = self.get_pnl() + self.initial_balance * max_loss_percent
        allocated_capital = cushion * multiplier
        return allocated_capital

    #Time Invariant Protection Portfolio (TIPP)
    def tipp_risk_manager(self, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = (self.get_pnl() + self.initial_balance) * max_loss_percent
        allocated_capital = cushion * multiplier
        return allocated_capital
    
    #Percent of remaining balance
    def ratio_risk_manager(self, ratio = 0.3):
        return self.balance*ratio

    #calculate how many shares to purchase based on risk manager type
    def purchase_size(self, price, size, symbol):
        balance_limit = self.balance/price
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager()/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager()/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager()/price
        else:
            risk_limit = balance_limit
        risk_limit-=self.long[symbol]

        print(size, balance_limit, risk_limit)
        return(min(size, min(balance_limit, risk_limit)))

    def buy(self, price, size, symbol):
        
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price
        
        print("Starting buy")

        # use risk management functionv
        shares_to_buy = self.purchase_size(price, size, symbol)

        self.balance -= shares_to_buy * price
        self.long[symbol] += shares_to_buy
        print("Bought " + str(shares_to_buy) + " shares of " + symbol + " at " + str(price))
        print("Finished buy")

    
        self.portfolio_lock.release()

        

    #calculate how many shares to sell based on risk manager type
    def sell_size(self, price, size, symbol):
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager()/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager()/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager()/price
        else:
            risk_limit = 0
        risk_limit-=(-self.long[symbol])

        print(size, risk_limit)
        return(min(size, risk_limit))
    
    def sell(self, price, size, symbol, fixed=None):
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price

        print("Starting sell")
        if not fixed:
            shares_to_sell = self.sell_size(price, size, symbol)
            #shares_to_sell = min(size, self.long[symbol])
        else:
            shares_to_sell = fixed

        self.balance += shares_to_sell * price
        self.long[symbol] -= shares_to_sell
        print("Sold " + str(shares_to_sell) + " shares of " + symbol + " at " + str(price))
        print("Finished sell")

        

        self.portfolio_lock.release()

        

    def rebalance(self, price, size, symbol):
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price

        print("Starting rebalance")
        risk_limit = None
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager()/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager()/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager()/price

        print(risk_limit)
        
        if risk_limit:
            if self.long[symbol] > risk_limit:
                self.sell(price, 0, symbol, min(self.long[symbol]-risk_limit, size))
                print("Rebalancing: Sold " + str(min(self.long[symbol]-risk_limit, size)) + " shares of " + symbol + " at " + str(price))
                self.portfolio_lock.release()
                return
        print("Rebalancing: no shares sold")
        print("Finished rebalance")

        

        self.portfolio_lock.release()


    def get_pnl(self):
        asset_value = 0
        for key in self.long:
            asset_value += self.long[key] * self.prices[key]

        pnl = (self.balance + asset_value) - self.initial_balance
        self.pnls.append(pnl)
        return pnl
    
    def get_available_balance(self):
        return self.balance