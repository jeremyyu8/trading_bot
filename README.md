# trading_bot

Systematic trading bot for cryptocurrencies that collects market data from Binance, Coinbase, and OKX exchanges and executes various strategies. Trading bot is fully configurable with CLI, i.e. can mix and match exchanges, coins, strategies, and risk management strategies.

**Functionalities:**

- Live trading: Strategies listen to coins on various exchanges and simulate executing trades (note: not trading real money) based on momentum, mean reversion, volatility, etc.
- Portfolio risk managing: Trade signals pass through a portfolio manager that manage risk using position sizing and trade risk allocation.
- Data collection: Bot has an option to switch to data collection mode over a set period of time; useful for future backtesting.
- Backtesting: Bot can run live stragies on .csv data collected using the data collection functionality.

**CLI Usage:**
Help:
![](/example/CLI_help.png)
Example configuration:
![](/example/CLI_example_config.png)
Trade notification example:
![](/example/CLI_example_trade_temp.png)

**Example Results Using MACD + Hurst Exponent Strategy on OKX Exchange:**

<!-- <!-- ![PNL from trading BTC, ETH on Coinbase and Binance for 2 hours](/example/pnl_plot.JPG) -->

![Trading various coins on OKX](/example/example_pnl.png)

**Signals used for strategies:**

- Moving Average Convergence/Divergence (MACD) + Hurst Exponent: MACD indicator identifies potential trend reversals or momentum shifts; Hurst exponent measures the long-term memory of a time series and persistence of trends.
- Relative Strength Index (RSI): Measures the speed and change of price movements; indicates either overbought or oversold for potential trend reverals.
- Simple Moving Average (SMA): Provides a smoothed line to identify potential trend continuation or mean reversion.
- Narrow Order Book Spread: If a new order comes in and makes the spread one tick wide, fill the order due to future price reversion.

**Risk managing strategies:**

- Constant Proportion Portfolio Insurance (CPPI): adjusts the allocation of positions between high risk and low risk (cash) instruments based on initial balance
- Time Invariant Protection Portfolio (TIPP): adjusts the allocation of positions between high risk and low risk (cash) instruments based on initial balance and overall PNL
- Constant Balance Proportion: approaches risk using a fixed ratio of available balance for trades

**Future ideas: perform correlation computations between derivatives, look for arbitrage opportunities between exchanges**
