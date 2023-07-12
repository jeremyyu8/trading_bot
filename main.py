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
                                    \nTry \'python main.py -e Binance Coinbase -c BTC ETH -s macd rsi -r tipp\' to simulate live trading BTC on Binance using macd, ETH on Coinbase using rsi, with tipp risk management\
                                    \nTry \'python main.py -e OKX -c ETH -d download\' to download ETH data from OKX")

exchanges = ['Binance', 'Coinbase', 'OKX']
cryptocurrencies = ['BTC', 'ETH', 'XRP', 'LTC', 'ADA']
trading_signals = ['macd', 'rsi', 'sma']
risk_strategies = ['cppi', 'tipp', 'ratio']
data_actions = ['live', 'historic', 'download']

parser.add_argument('-e', '--exchanges', choices=exchanges, nargs='*', help='Select exchanges (at least one)')
parser.add_argument('-c', '--currencies', choices=cryptocurrencies, nargs='*', help='Select cryptocurrencies (at least one)')
parser.add_argument('-s', '--trading_signals', choices=trading_signals, nargs='*', help='Select trading strategies (at least one, unless data action is download)')
parser.add_argument('-r', '--risk_manager', choices=risk_strategies, type = str, help='Select a risk management strategy (default: cppi)', default="cppi")
parser.add_argument('-d', '--data_action', choices=data_actions, type = str, help = 'Select data actions (default: \'live\')', default="live")
parser.add_argument('-b', '--balance', type = float, help = 'Select initial balance (default: 1000000)', default=1000000)

args = parser.parse_args()

#function to initialize everything using parsed args
def initialize_bot(args):
    #dictionary for mapping currencies to exchange-specific symbol names
    exchange_to_symbol = {"Binance": {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "XRP": "XRPUSDT", "LTC":"LTCUSDT", "ADA": "ADAUSDT"}, 
                  "Coinbase": {"BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "LTC": "LTC-USD", "ADA": "ADA-USD"}, 
                  "OKX": {"BTC": "BTC-USDT", "ETH": "ETH-USDT", "XRP": "XRP-USDT", "LTC": "LTC-USDT", "ADA": "ADA-USDT"}}

    #initialize portfolio/risk manager
    all_equities = list(set([exchange_to_symbol[exchange][currency] for exchange, currency in zip(args.exchanges, args.currencies)]))
    if args.data_action != "download": portfolio_manager = PortfolioManager(initial_balance=args.balance, risk_manager=args.risk_manager, equities=all_equities)

    #initialize exchange specific data managers
    binance_data_manager = BinanceDataManager()
    coinbase_data_manager = CoinbaseDataManager()
    okx_data_manager = OkxDataManager()
    
    trading_signals = args.trading_signals if args.trading_signals else [None] * len(args.exchanges)

    #initialize (exchange, currency, strategy) connections
    for exchange, currency, strategy in zip(args.exchanges, args.currencies, trading_signals):
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
                binance_data_manager.add_symbol_handler(symbol=symbol, type=args.data_action) 
                if args.data_action != "download": binance_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance)
            case 'Coinbase':
                strategy_instance = None 
                match strategy:
                    case 'macd':
                        strategy_instance = MACDStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                    case 'rsi':
                        strategy_instance = RSIStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                    case 'sma': 
                        strategy_instance = SimpleMovingAvgStrategy(market_data_manager=coinbase_data_manager, portfolio_manager=portfolio_manager) 
                coinbase_data_manager.add_symbol_handler(symbol=symbol, type=args.data_action) 
                if args.data_action != "download": coinbase_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance) 
            case 'OKX':
                strategy_instance = None 
                match strategy:
                    case 'macd':
                        strategy_instance = MACDStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                    case 'rsi':
                        strategy_instance = RSIStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                    case 'sma': 
                        strategy_instance = SimpleMovingAvgStrategy(market_data_manager=okx_data_manager, portfolio_manager=portfolio_manager) 
                okx_data_manager.add_symbol_handler(symbol=symbol, type=args.data_action) 
                if args.data_action != "download": okx_data_manager.get_orderbook(symbol).add_book_listener(strategy=strategy_instance)
    
    #listener function for esc key press to stop script
    def on_press(key):
        if key == keyboard.Key.esc:
            if args.data_action != "download": portfolio_manager.plot()
            os._exit(0)
        else:
            print("A key has been pressed. Press esc if you are trying to exit.")

    #use threading to start data manager for each exchange
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(args.exchanges)+1) as executor:
        if 'Binance' in args.exchanges: 
            executor.submit(binance_data_manager.start)
        if 'Coinbase' in args.exchanges: 
            executor.submit(coinbase_data_manager.start)
        if 'OKX' in args.exchanges: 
            executor.submit(okx_data_manager.start)
        listener = keyboard.Listener(on_press=on_press)
        executor.submit(listener.start)
    
    
#check paramters and print configuration
if (args.data_action != "download" and args.exchanges and args.currencies and args.trading_signals and len(args.exchanges) == len(args.currencies) == len(args.trading_signals)) or (args.data_action == "download" and args.exchanges and args.currencies and len(args.exchanges) == len(args.currencies)):
    print("(Press esc to exit at any time)")
    print()
    if args.data_action == "download" and args.trading_signals:
        print("Warning, trading signals will not be used because data action is download")
    print('Configuration successful for:')


    for i in range(len(args.exchanges)):
        match args.data_action:
            case 'live':
                print(f"Live trading {args.currencies[i]} using {args.trading_signals[i]} signals on {args.exchanges[i]} exchange")
            case 'historic':
                print(f"Historic trading {args.currencies[i]} using {args.trading_signals[i]} signals on {args.exchanges[i]} exchange")
            case 'download':
                print(f"Downloading {args.currencies[i]} data on {args.exchanges[i]} exchange")
    if args.data_action != "download": print(f"Using {args.risk_manager} risk manager, initial balance is {args.balance}")
    print()

    #initialize trading bot
    initialize_bot(args=args)

else: 
    #if configuration wrong, output what extra info is needed
    if not args.exchanges: 
        print("Need exchanges")
    if not args.currencies:
        print("Need currencies")
    if not args.trading_signals and args.data_action != "download":
        print("Need trading signals when not downloading data")
        
    if args.exchanges and args.currencies and args.trading_signals and not (len(args.exchanges) == len(args.currencies) == len(args.trading_signals)):
        print(f"Mismatching lengths; need same number of exchanges, currencies, signal strategies; current lengths {len(args.exchanges)}, {len(args.currencies)}, {len(args.trading_signals)}")
    elif args.data_action == "download" and args.exchanges and args.currencies and not (len(args.exchanges) == len(args.currencies)):
        print(f"Mismatching lengths; need same number of exchanges, currencies; current lengths {args.exchanges}, {args.currencies}")


        