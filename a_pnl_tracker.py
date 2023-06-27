class PNLTracker():
    def __init__(self, initial_balance) -> None:
        self.long = 0
        self.short = 0
        self.initial_balance = initial_balance
        self.balance = initial_balance 

    def buy(self, price, size):
        shares_to_buy = min(size, self.balance/price) # use risk management function
        self.balance -= shares_to_buy * price
        self.long += shares_to_buy

    def sell(self, price, size):
        shares_to_sell = min(size, self.long)
        self.balance += shares_to_sell * price
        self.long -= shares_to_sell 

    def get_balance(self, price):
        return (self.balance + self.long*price) - self.initial_balance