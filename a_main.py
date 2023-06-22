from a_market_data_manager import OkxDataManager 
from a_pnl_tracker import PNLTracker

from a_strategy import MovingAvgStrategy, RSIStrategy

OKX_data_manager = OkxDataManager(symbols=["BTC-USDT"], types=["live"])
PNL_tracker = PNLTracker(initial_balance=1000000)

OKX_data_manager.start()