from market_data_manager import BinanceDataManager, CoinbaseDataManager, OkxDataManager 
from portfolio_manager import PortfolioManager
from strategy import SimpleMovingAvgStrategy, RSIStrategy, MACDStrategy

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
                                 description="Systematic trading bot configuration: Exchanges, Coins, and Strategies are paired up in the order they are provided as arguments\
                                    \nTry \'python main.py -e Binance -c BTC -s macd\' to trade BTC on Binance using macd signals\
                                    \nTry \'python main.py -e Binance Coinbase -c BTC ETH -s macd rsi -r tipp\' to trade BTC on Binance using macd, ETH on Coinbase using rsi, with tipp risk management")

exchanges = ['Binance', 'Coinbase', 'OKX']
cryptocurrencies = ['BTC', 'ETH', 'XRP', 'LTC', 'ADA']
trading_strategies = ['macd', 'rsi', 'sma']
risk_strategies = ['cppi', 'tipp', 'ratio']

parser.add_argument('-e', '--exchanges', choices=exchanges, nargs='*', help='Select exchanges (at least one)')
parser.add_argument('-c', '--currencies', choices=cryptocurrencies, nargs='*', help='Select cryptocurrencies (at least one)')
parser.add_argument('-s', '--signal_strategies', choices=trading_strategies, nargs='*', help='Select trading strategies (at least one)')
parser.add_argument('-r', '--risk-strategy', choices=risk_strategies, type = str, help='Select a risk management strategy (default: cppi)', default="cppi")

args = parser.parse_args()

if len(args.exchanges) == len(args.currencies) == len(args.signal_strategies):
    for i in range(len(args.exchanges)):
        print(f"Trading {args.currencies[i]} using {args.signal_strategies[i]} signals on {args.exchanges[i]} exchange")
else: 
    print(f"Mismatching lengths; need same number of exchanges, currencies, signal strategies, currently {args.exchanges}, {args.currencies}, {args.signal_strategies}")


equity_mapping = {"Binance": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "XRP": "XRPUSDT", "LTC":"LTCUSDT", "ADA": "ADAUSDT"}, 
                  "Coinbase": {"BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "LTC": "LTC-USD", "ADA": "ADA-USD"}, 
                  "OKX": {"BTC": "BTC-USDT", "ETH": "ETH-USDT", "XRP": "XRP-USDT", "LTC": "LTC-USDT", "ADA": "ADA-USDT"}}




#---------PARAMETERS----------
#equities/symbol that will be traded
equities = ["BTC-USDT", "ETH-USDT", "LTC-USDT", "XRP-USDT", "BNB-USDT", "ADA-USDT", "SOL-USDT", "TRX-USDT", "DOT-USDT", "UNI-USDT"]

#strategies for respective equities/symbol (sma, rsi, macd)
strategies = ["rsi", "rsi", "sma", "rsi", "macd", "macd", "rsi", "macd", "sma", "rsi"]

#type of data (live, historic, or download)
data_type = "live"

#risk manager (cppi, tipp, ratio)
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
#OKX_data_manager.start()

########## TEMP #########

# Binance_data_manager = BinanceDataManager(symbols = ["btcusdt"], types = ["live"])
# portfolio_manager = PortfolioManager(initial_balance=initial_balance, risk_manager=risk_manager, equities=["btcusdt"])
# sma = SimpleMovingAvgStrategy(market_data_manager=Binance_data_manager, portfolio_manager=portfolio_manager)
# Binance_data_manager.get_orderbook("btcusdt").add_book_listener(strategy = sma)
# Binance_data_manager.start()

Coinbase_data_manager = CoinbaseDataManager(symbols = ["BTC-USD"], types = ["live"])
portfolio_manager = PortfolioManager(initial_balance=initial_balance, risk_manager=risk_manager, equities=["btcusdt"])
sma = SimpleMovingAvgStrategy(market_data_manager=Coinbase_data_manager, portfolio_manager=portfolio_manager)
Coinbase_data_manager.get_orderbook("BTC-USD").add_book_listener(strategy = sma)
#Coinbase_data_manager.start()



#####################

        