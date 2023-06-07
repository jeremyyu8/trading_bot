import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
from datetime import datetime

from main import make_okx_api_call

# api limit is 20 requests/2 seconds

################# HELPER FUNCS ########################


def get_historical(instId, after='', before='', bar='', limit=''):
    '''
    Self explanatory, basic usage example:

    instId = 'BTC-USD'
    dt = datetime(2023, 6, 1, 12, 1, 12) #year, month, day, minute, hour, second
    historical = get_historical(instId, after = timestamp(dt), bar = '1m', limit = 10)
    visualize_historical(historical)

    '''

    params = {'instId': instId, 'after': str(after), 'before': str(
        before), 'bar': bar, 'limit': str(limit)}
    request = make_okx_api_call(
        '/api/v5/market/history-index-candles', params=params)

    historical = pd.DataFrame(request['data'])

    historical.columns = ["Date", "Open", "High", "Low", "Close", "State"]
    historical = historical.drop('State', axis=1)
    historical['Date'] = pd.to_datetime(historical['Date'], unit='ms')

    # cast to floats lol
    historical['Open'] = historical['Open'].astype(float)
    historical['High'] = historical['High'].astype(float)
    historical['Low'] = historical['Low'].astype(float)
    historical['Close'] = historical['Close'].astype(float)

    historical.set_index('Date', inplace=True)
    historical.sort_values(by='Date')
    return historical


def visualize_historical(data):
    mpf.plot(data, type='candle', title='Candlestick Chart')


def timestamp(dt):
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000)

########################################################################################


def moving_average_strategy_candles(data, window_size):
    """
    Implements a simple moving average strategy using candlestick data.

    Parameters:
    - data: A DataFrame containing candlestick data with columns 'open', 'high', 'low', and 'close'.
    - window_size: The size of the moving average window.

    Returns:
    - An array of signals (1 for buy, -1 for sell, 0 for hold).
    """
    signals = np.zeros(len(data))
    moving_avg = data['Close'].rolling(window=window_size).mean()

    for i in range(window_size, len(data)):
        if data['Close'].iloc[i] > moving_avg.iloc[i - window_size]:
            signals[i] = -1
        elif data['Close'].iloc[i] < moving_avg.iloc[i - window_size]:
            signals[i] = 1

    return signals


def calculate_rsi(deltas, period):
    '''
    Calculates Relative Strength Index (0-100)

    Parameters:
    - deltas: A list containing the n most recent changes in close price
    - period: Number of most recent close prices used in rsi calculation

    Returns:
    - RSI value
    '''

    # rsi calculation using simple moving avg
    total_change = [0, 0]
    for d in deltas:
        if d > 0:
            total_change[0] += d
        else:
            total_change[1] += d
    avg_ups = total_change[0]/period
    avg_downs = abs(total_change[1])/period
    relative_strength = avg_ups/avg_downs
    rsi = 100 - 100 / (1+relative_strength)
    return rsi


def rsi_strategy(data, period, buy_thresh, sell_thresh):
    '''
    Implements a simple relative strength index strategy using candlestick data.
    >=sell_thresh -> sell, <=buy_thresh -> buy

    Parameters:
    - data: A DataFrame containing candlestick data with columns 'open', 'high', 'low', and 'close'.
    - period: Number of most recent close prices used in rsi calculation

    Returns:
    - An array of signals (1 for buy, -1 for sell, 0 for hold).

    '''
    signals = np.zeros(len(data))

    # get deltas
    data['PriceChange'] = data['Close'].diff().fillna(0).round(2)

    for i in range(0, len(data)-period):
        deltas = data['PriceChange'].tolist()[i:i+period]
        rsi = calculate_rsi(deltas, period)
        if rsi <= buy_thresh:
            signals[i+period] = 1
        elif rsi >= sell_thresh:
            signals[i+period] = -1

    return signals


def mean_reversion_strategy(symbol, period):
    '''
    Not sure
    '''
    pass


def simulate_strategy_historical(symbol, strategy, initial_balance, start_date, end_date):
    '''
    Not done
    '''
    pnl = []
    balance = initial_balance
    shares = 0
    spot_prices = get_historical(
        symbol, start_date, bar='1m', limit=100)  # fix

    signals = rsi_strategy(spot_prices, period=14,
                           buy_thresh=30, sell_thresh=70)

    assert len(signals) == len(spot_prices)

    for i in range(len(signals)):
        curr_price = int(spot_prices['Close'][i])
        if signals[i] == 1:
            # buy
            if (balance // curr_price) == 0:
                continue
            shares += balance // curr_price
            balance -= shares * curr_price
        elif signals[i] == -1:
            # sell
            balance += shares * curr_price
            shares = 0

        pnl.append(balance+shares*curr_price)

        if balance <= 0:
            print('Bankrupt!')
            break

    return pnl


# Example usage
instId = 'BTC-USD'
dt = datetime(2023, 6, 1, 12, 1, 12)  # year, month, day, minute, hour, second
data = get_historical(instId, after=timestamp(dt), bar='1m', limit=100)
# visualize_historical(data)
print(data)

signals = moving_average_strategy_candles(data, window_size=5)
print("Trading Signals:", signals)

signals = rsi_strategy(data, period=14, buy_thresh=30, sell_thresh=70)
print("Trading Signals:", signals)

pnl = simulate_strategy_historical(
    symbol='BTC-USD', strategy='', initial_balance=100000, start_date=timestamp(datetime(2023, 6, 1, 8, 1, 12)), end_date='')
print(pnl)
