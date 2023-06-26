from a_market_data_manager import OkxDataManager 
from a_pnl_tracker import PNLTracker

from a_strategy import MovingAvgStrategy, RSIStrategy

#OKX_data_manager = OkxDataManager(symbols=["BTC-USDT", "LTC-USDT", "ETH-USDT"], types=["live", "live", "live"])

#initialize data manager, strategies, pnl tracker
OKX_data_manager = OkxDataManager(symbols=["BTC-USDT"], types=["live"])
PNL_tracker = PNLTracker(initial_balance=1000000)
moving_avg = MovingAvgStrategy(market_data_manager=OKX_data_manager, pnl_tracker=PNL_tracker)

#assign strategies to listen to specific orderbooks
OKX_data_manager.get_orderbook("BTC-USDT").add_book_listener(strategy=moving_avg)

#start all strategies
OKX_data_manager.start()


        