class PortfolioManager():
    def __init__(self, initial_balance, risk_manager) -> None:
        self.long = 0
        self.short = 0
        self.initial_balance = initial_balance
        self.balance = initial_balance 
        self.risk_manager = risk_manager
        self.convex_risk_manager_equity = 0

    #Constant Proportion Portfolio Insurance (CPPI)
    def cppi_risk_manager(self, price, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = self.get_pnl(price) + self.initial_balance * max_loss_percent
        allocated_capital = cushion * multiplier
        return allocated_capital

    #Time Invariant Protection Portfolio (TIPP)
    def tipp_risk_manager(self, price, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = (self.balance + self.long*price) * max_loss_percent
        allocated_capital = cushion * multiplier
        return allocated_capital
    
    #Percent of remaining balance
    def ratio_risk_manager(self, price, ratio = 0.3):
        return self.balance*ratio


    def purchase_size(self, price, size):
        balance_limit = self.balance/price
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager(price)/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager(price)/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager(price)/price
        else:
            risk_limit = balance_limit
        risk_limit-=self.long

        print(size, balance_limit, risk_limit)
        return(min(size, min(balance_limit, risk_limit)))

    def buy(self, price, size):
        # use risk management function
        shares_to_buy = self.purchase_size(price, size)
        self.balance -= shares_to_buy * price
        self.long += shares_to_buy
        print("Bought " + str(shares_to_buy) + " shares at " + str(price))

    def sell(self, price, size, fixed=None):
        if not fixed:
            shares_to_sell = min(size, self.long)
        else:
            shares_to_sell = fixed
        self.balance += shares_to_sell * price
        self.long -= shares_to_sell
        print("Sold " + str(shares_to_sell) + " shares at " + str(price))

    def rebalance(self, price, size):
        risk_limit = None
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager(price)/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager(price)/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager(price)/price
        
        if risk_limit:
            if self.long > risk_limit:
                self.sell(price, 0, min(self.long-risk_limit, size))
                print("Rebalancing: Sold " + str(min(self.long-risk_limit, size)) + " shares at " + str(price))

    def get_pnl(self, price):
        return (self.balance + self.long*price) - self.initial_balance
    
    def get_available_balance(self):
        return self.balance