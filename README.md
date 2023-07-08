# trading_bot

Crypto systematic trading bot that collects market data from Binance and OKX exchanges and executes various strategies. Bot is fully configurable, i.e. can mix and match exchanges, coins, strategies, and risk managers.

Functionalities:

- Live trading: Strategies listen to coins on various exchanges and simulate executing trades (note: not trading real money) based on momentum, mean reversion, volatility, etc.
- Portfolio risk managing: Trade signals pass through a portfolio manager that manage risk using position sizing and trade risk allocation.
- Data collection: Bot has an option to switch to data collection mode over a set period of time; useful for future backtesting.
- Backtesting: Bot can run live stragies on .csv imported data, typically collected using the data collection functionality.

Strategies implemented:

- Moving Average Convergence/Divergence (MACD) + Hurst Exponent: brief explanation
- Relative Strength Index (RSI): brief explanation
- Simple Moving Average (SMA): brief expl

Risk managing stragies:

- Constant Proportion Portfolio Insurance (CPPI): sad
- Time Invariant Protection Portfolio (TIPP): asd
- Constant Balance Proportion: ads

Future ideas: correlation computations between derivatives, looking for arbitrage opportunities between exchanges
