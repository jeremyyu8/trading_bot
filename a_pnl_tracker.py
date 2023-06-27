class PNLTracker():
    def __init__(self, initial_balance) -> None:
        self.balance = initial_balance 

    def buy(self, amount):
        self.balance -= amount 

    def sell(self, amount):
        self.balance += amount 

    def get_balance(self):
        return self.balance