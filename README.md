# trading_bot

Crypto systematic trading bot that collects market data from Binance and OKX exchanges and executes various strategies. Bot is fully configurable with CLI, i.e. can mix and match exchanges, coins, trade signals, and risk management strategies.

Functionalities:

- Live trading: Strategies listen to coins on various exchanges and simulate executing trades (note: not trading real money) based on momentum, mean reversion, volatility, etc.
- Portfolio risk managing: Trade signals pass through a portfolio manager that manage risk using position sizing and trade risk allocation.
- Data collection: Bot has an option to switch to data collection mode over a set period of time; useful for future backtesting.
- Backtesting: Bot can run live stragies on .csv imported data, typically collected using the data collection functionality.

CLI Usage:
![Setup for trading BTC, ETH on Coinbase and Binance for 2 hours](/example/CLI_example_config.png)
![Setup for trading BTC, ETH on Coinbase and Binance for 2 hours](/example/CLI_help.png)

Example Results:

<!-- ![PNL from trading BTC, ETH on Coinbase and Binance for 2 hours](/example/pnl_plot.JPG)
![Net position for BTC, ETH on Coinbase](/example/pnl_plot.JPG) -->

Signals used for strategies:

- Moving Average Convergence/Divergence (MACD) + Hurst Exponent: MACD indicator identifies potential trend reversals or momentum shifts; Hurst exponent measures the long-term memory of a time series and persistence of trends.
- Relative Strength Index (RSI): Measures the speed and change of price movements; indicates either overbought or oversold for potential trend reverals.
- Simple Moving Average (SMA): Provides a smoothed line to identify potential trend continuation or mean reversion.
- Narrow Order Book Spread: If a new order comes in and makes the spread one tick wide, fill the order due to future price reversion.

Risk managing strategies:

- Constant Proportion Portfolio Insurance (CPPI): adjusts the allocation of positions between high risk and low risk instruments
- Time Invariant Protection Portfolio (TIPP): maintains fixed allocation of assets accross instruments, ignoring market conditions
- Constant Balance Proportion: approaches risk using a fixed allocation ratio between risky and risk-free assets and periodic rebalancing

Future ideas: perform correlation computations between derivatives, look for arbitrage opportunities between exchanges
