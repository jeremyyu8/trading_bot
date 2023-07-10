from market_data_manager import BinanceDataManager, CoinbaseDataManager, OkxDataManager 
from portfolio_manager import PortfolioManager
from strategy import SimpleMovingAvgStrategy, RSIStrategy, MACDStrategy
import concurrent.futures
import argparse
from pynput import keyboard
import os

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
                                 description="Systematic trading bot configuration: Exchanges, Coins, and Strategies are paired up in the order they are provided as arguments\
                                    \nTry \'python main.py -e Binance -c BTC -s macd\' to simulate live trading BTC on Binance using macd signals\
                                    \nTry \'python main.py -e Binance Coinbase -c BTC ETH -s macd rsi -r tipp\' to simulate live trading BTC on Binance using macd, ETH on Coinbase using rsi, with tipp risk management")

exchanges = ['Binance', 'Coinbase', 'OKX']
cryptocurrencies = ['BTC', 'ETH', 'XRP', 'LTC', 'ADA']
trading_signals = ['macd', 'rsi', 'sma']
risk_strategies = ['cppi', 'tipp', 'ratio']
data_actions = ['live', 'historic', 'download']

parser.add_argument('-e', '--exchanges', choices=exchanges, nargs='*', help='Select exchanges (at least one)')
parser.add_argument('-c', '--currencies', choices=cryptocurrencies, nargs='*', help='Select cryptocurrencies (at least one)')
parser.add_argument('-s', '--trading_signals', choices=trading_signals, nargs='*', help='Select trading strategies (at least one)')
parser.add_argument('-r', '--risk_manager', choices=risk_strategies, type = str, help='Select a risk management strategy (default: cppi)', default="cppi")
parser.add_argument('-d', '--data_actions', choices=data_actions, nargs='*', help = 'Select data actions (default: \'live\' for everything)')
parser.add_argument('-b', '--balance', type = float, help = 'Select initial balance (default: 1000000)', default=1000000)

args = parser.parse_args()

#function to initialize everything using parsed args
def initialize_bot(args):
    print(args.exchanges)
    print(args.currencies)
    print(args.trading_signals)
    print(args.risk_manager)
    print(args.data_actions)
    print(args.balance)
    assert len(args.exchanges) == len(args.currencies) == len(args.trading_signals)

    #dictionary for mapping currencies to exchange-specific symbol names
    exchange_to_symbol = {"Binance": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "XRP": "XRPUSDT", "LTC":"LTCUSDT", "ADA": "ADAUSDT"}, 
                  "Coinbase": {"BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "LTC": "LTC-USD", "ADA": "ADA-USD"}, 
                  "OKX": {"BTC": "BTC-USDT", "ETH": "ETH-USDT", "XRP": "XRP-USDT", "LTC": "LTC-USDT", "ADA": "ADA-USDT"}}


    #initialize portfolio/risk manager
    all_equities = list(set([exchange_to_symbol[exchange][currency] for exchange, currency in zip(args.exchanges, args.currencies)]))
    portfolio_manager = PortfolioManager(initial_balance=args.balance, risk_manager=args.risk_manager, equities=all_equities)

    #initialize exchange specific data managers
    binance_data_manager = BinanceDataManager()
    coinbase_data_manager = CoinbaseDataManager()
    okx_data_manager = OkxDataManager()
    
    #set up data actions for future convenience
    data_actions = args.data_actions if args.data_actions else ['live' for _ in range(len(args.exchanges))]

    #initialize (exchange, currency, strategy) connections
    for exchange, currency, strategy, data_action in zip(args.exchanges, args.currencies, args.trading_signals, data_actions):
        print(exchange, currency, strategy, data_action)
        symbol = exchange_to_symbol[exchange][currency]
        match exchange:
            case 'Binance':
                strategy_instance = None 
                match strategy:
                    case 'macd':
                        strategy_instance = MACDStrategy(market_data_manager=binance_data_manager, portfolio_manager=portfolio_manager) 
                    case 'rsi':
                        strategy_instance = RSIStrategy(market_data_manager=binance_data_manager, portfolio_manager=portfolio_manager) 
                    case 'sma': 
                        strategy_instance = SimpleMovingAvgStrategy(market_data_manager=binance_data_manager, portfolio_manager=portfolio_manager) 
                binance_data_manager.add_symbol_handler(symbol=symbol, type=data_action) 
                binance_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance)
            case 'Coinbase':
                strategy_instance = None 
                match strategy:
                    case 'macd':
                        strategy_instance = MACDStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                    case 'rsi':
                        strategy_instance = RSIStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                    case 'sma': 
                        strategy_instance = SimpleMovingAvgStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                coinbase_data_manager.add_symbol_handler(symbol=symbol, type=data_action) 
                coinbase_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance) 
            case 'OKX':
                strategy_instance = None 
                match strategy:
                    case 'macd':
                        strategy_instance = MACDStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                    case 'rsi':
                        strategy_instance = RSIStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                    case 'sma': 
                        strategy_instance = SimpleMovingAvgStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                okx_data_manager.add_symbol_handler(symbol=symbol, type=data_action) 
                okx_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance)
    
    def on_press(self, key):
        if key == keyboard.Key.esc:
            os._exit(0)

    #start data collection and trading
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(args.exchanges)+1) as executor:
        if 'Binance' in args.exchanges: 
            executor.submit(binance_data_manager.start)
        if 'Coinbase' in args.exchanges: 
            executor.submit(coinbase_data_manager.start)
        if 'OKX' in args.exchanges: 
            executor.submit(okx_data_manager.start)
        listener = keyboard.Listener(on_press=on_press)
        executor.submit(listener.start)
    
    
    
if args.exchanges and (not args.data_actions or len(args.exchanges) == len(args.currencies) == len(args.trading_signals) == len(args.data_actions)):
    data_actions = args.data_actions if args.data_actions else ['live' for _ in range(len(args.exchanges))]
    print("(Press esc to exit at any time)")
    print()
    print('Configuration successful for:')


    for i in range(len(args.exchanges)):
        match data_actions[i]:
            case 'live':
                print(f"Live trading {args.currencies[i]} using {args.trading_signals[i]} signals on {args.exchanges[i]} exchange")
            case 'historic':
                print(f"Historic trading {args.currencies[i]} using {args.trading_signals[i]} signals on {args.exchanges[i]} exchange")
            case 'download':
                print(f"Downloading {args.currencies[i]} data on {args.exchanges[i]} exchange")
    print()

    initialize_bot(args=args)

else: 
    if not args.exchanges or not args.currencies or args.trading_signals:
        print("Need exchanges, currencies, and signals")
    elif args.data_actions:
        print(f"Mismatching lengths; need same number of exchanges, currencies, signal strategies; currently {args.exchanges}, {args.currencies}, {args.signal_strategies}")
    else:
        print(f"Mismatching lengths; need same number of exchanges, currencies, signal strategies, data actions; currently {args.exchanges}, {args.currencies}, {args.signal_strategies}, {args.data_actions}")




########## TEMP #########

# Binance_data_manager = BinanceDataManager(symbols = ["btcusdt"], types = ["live"])
# portfolio_manager = PortfolioManager(initial_balance=100000, risk_manager="cppi", equities=["btcusdt"])
# sma = SimpleMovingAvgStrategy(market_data_manager=Binance_data_manager, portfolio_manager=portfolio_manager)
# Binance_data_manager.get_orderbook("btcusdt").add_book_listener(strategy = sma)
# Binance_data_manager.start()

# Coinbase_data_manager = CoinbaseDataManager(symbols = ["BTC-USD"], types = ["live"])
# portfolio_manager = PortfolioManager(initial_balance=initial_balance, risk_manager=risk_manager, equities=["btcusdt"])
# sma = SimpleMovingAvgStrategy(market_data_manager=Coinbase_data_manager, portfolio_manager=portfolio_manager)
# Coinbase_data_manager.get_orderbook("BTC-USD").add_book_listener(strategy = sma)
#Coinbase_data_manager.start()


        