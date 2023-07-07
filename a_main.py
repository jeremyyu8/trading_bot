from a_market_data_manager import OkxDataManager 
from a_portfolio_manager import PortfolioManager

from a_strategy import SimpleMovingAvgStrategy, RSIStrategy, MACDStrategy

#---------PARAMETERS----------
#equities/symbol that will be traded
equities = ["BTC-USDT", "ETH-USDT", "LTC-USDT", "XRP-USDT", "BNB-USDT", "ADA-USDT", "SOL-USDT", "TRX-USDT", "DOT-USDT", "UNI-USDT"]

#strategies for respective equities/symbol (sma, rsi, macd)
strategies = ["rsi", "rsi", "sma", "rsi", "macd", "macd", "rsi", "macd", "sma", "rsi"]

#type of data (live, historic, or download)
data_type = "live"

#risk manager (cipp, tipp, ratio)
risk_manager = "tipp"

#initial balance for trading
initial_balance = 1000000
#-----------------------------


#initialize data manager, portfolio manager
types = [data_type for i in range(len(equities))]
OKX_data_manager = OkxDataManager(symbols=equities, types=types)
portfolio_manager = PortfolioManager(initial_balance=initial_balance, risk_manager=risk_manager, equities=equities)

#initialize strategies
sma = SimpleMovingAvgStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)
rsi = RSIStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)
macd = MACDStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)

#assign strategies to listen to specific orderbooks
for i, equity in enumerate(equities):
    if strategies[i] == "sma":
        OKX_data_manager.get_orderbook(equity).add_book_listener(strategy=sma)
    elif strategies[i] == "rsi":
        OKX_data_manager.get_orderbook(equity).add_book_listener(strategy=rsi)
    elif strategies[i] == "macd":
        OKX_data_manager.get_orderbook(equity).add_book_listener(strategy=macd)
    else:
        print("INVALID STRATEGY")
    
#start all strategies
OKX_data_manager.start()


        