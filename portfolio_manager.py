import threading
from pynput import keyboard
import matplotlib.pyplot as plt
from datetime import datetime 
import json 

class PortfolioManager():
    '''
    Manages risk among all strategies, tracks positions and PNL over all strategies and exchanges
    '''

    def __init__(self, initial_balance, risk_manager, equities) -> None:
        self.net_positions = {equity: 0 for equity in equities}
        self.prices = {equity: 0 for equity in equities}
        self.initial_balance = initial_balance
        self.balance = initial_balance 
        self.risk_manager = risk_manager
        self.pnls_over_time = []
        self.net_position_values_over_time = {equity: [] for equity in equities}
        self.portfolio_lock = threading.Lock()
        self.start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    #Constant Proportion Portfolio Insurance (CPPI)
    def cppi_risk_manager(self, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = self.get_pnl_without_save() + self.initial_balance * max_loss_percent
        allocated_capital = cushion * multiplier
        return allocated_capital

    #Time Invariant Protection Portfolio (TIPP)
    def tipp_risk_manager(self, max_loss_percent = 0.1, max_asset_downside = 0.2):
        multiplier = 1/max_asset_downside
        cushion = (self.get_pnl_without_save() + self.initial_balance) * max_loss_percent
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
        risk_limit-=self.net_positions[symbol]

        return max(0, min(size, min(balance_limit, risk_limit)))

    def buy(self, price, size, symbol):
        #aquire lock to prevent two executed trades changing balance at same time
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price
        

        print("Starting buy")
        # use risk management function to calculate purchas size
        shares_to_buy = self.purchase_size(price, size, symbol)

        #update positions and balance
        self.balance -= shares_to_buy * price
        self.net_positions[symbol] += shares_to_buy
        print("Bought " + str(shares_to_buy) + " shares of " + symbol + " at " + str(price))
        print("Finished buy")

        #release lock when done
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
        risk_limit-=(-self.net_positions[symbol])

        return max(0, min(size, risk_limit))
    
    def sell(self, price, size, symbol, fixed=None):
        #aquire lock to prevent two executed trades changing balance at same time
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price

        print("Starting sell")
        #use risk management function to get sell size
        if not fixed:
            shares_to_sell = self.sell_size(price, size, symbol)
        else:
            shares_to_sell = fixed

        #update positions and balance
        self.balance += shares_to_sell * price
        self.net_positions[symbol] -= shares_to_sell
        print("Sold " + str(shares_to_sell) + " shares of " + symbol + " at " + str(price))
        print("Finished sell")

        #release lock when done
        self.portfolio_lock.release()

        

    def rebalance(self, price, size, symbol):
        #aquire lock to prevent two executed trades changing balance at same time
        self.portfolio_lock.acquire()

        #update price for pnl calculation
        self.prices[symbol] = price

        print("Starting portfolio rebalance")
        #get risk limit from risk manager
        risk_limit = None
        if self.risk_manager == "cppi":
            risk_limit = self.cppi_risk_manager()/price
        elif self.risk_manager == "tipp":
            risk_limit = self.tipp_risk_manager()/price
        elif self.risk_manager == "ratio":
            risk_limit = self.ratio_risk_manager()/price

        #rebalance equities accordingly
        if risk_limit:
            if self.net_positions[symbol] > risk_limit:
                print("Finished rebalance: selling shares now")
                self.portfolio_lock.release()

                self.sell(price, 0, symbol, min(self.net_positions[symbol]-risk_limit, size))
                return
        print("Finished rebalance: no shares sold")

        #release lock when done
        self.portfolio_lock.release()


    #calculate pnl and append to pnl over time list
    def get_pnl(self):
        asset_value = 0
        for key in self.net_positions:
            cur_equity_value = self.net_positions[key] * self.prices[key]
            self.net_position_values_over_time[key].append(cur_equity_value)
            asset_value += cur_equity_value

        pnl = (self.balance + asset_value) - self.initial_balance
        self.pnls_over_time.append(pnl)
        return pnl
    
    #get pnl without saving to list
    def get_pnl_without_save(self):
        asset_value = 0
        for key in self.net_positions:
            cur_equity_value = self.net_positions[key] * self.prices[key]
            asset_value += cur_equity_value
        return (self.balance + asset_value) - self.initial_balance

    #plot pnl over time after exiting
    def plot(self):
        finish_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        plt.figure(figsize=(12,6))
        plt.plot(self.pnls_over_time, linewidth=2, label="PNL")
        for equity in self.net_position_values_over_time:
            # print(self.net_position_values_over_time[equity])
            plt.plot(self.net_position_values_over_time[equity], label = equity)

        plt.xlabel('time')
        plt.ylabel('USD')
        plt.title(f'Plot of PNLS and Net Positions from {self.start_time} to {finish_time}')
        plt.legend()
        plt.show()