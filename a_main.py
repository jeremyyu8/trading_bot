from a_market_data_manager import OkxDataManager 
from a_portfolio_manager import PortfolioManager

from a_strategy import SimpleMovingAvgStrategy, RSIStrategy, MACDStrategy

#OKX_data_manager = OkxDataManager(symbols=["BTC-USDT", "LTC-USDT", "ETH-USDT"], types=["live", "live", "live"])

#initialize data manager, strategies, pnl tracker
OKX_data_manager = OkxDataManager(symbols=["BTC-USDT"], types=["live"])
portfolio_manager = PortfolioManager(initial_balance=1000000, risk_manager="tipp")
#sma = SimpleMovingAvgStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)
#rsi = RSIStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)
macd = MACDStrategy(market_data_manager=OKX_data_manager, portfolio_manager=portfolio_manager)

#assign strategies to listen to specific orderbooks
OKX_data_manager.get_orderbook("BTC-USDT").add_book_listener(strategy=macd)

#start all strategies
OKX_data_manager.start()


        