import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
from datetime import datetime
import tensorflow as tf

from main import make_okx_api_call

# api limit is 20 requests/2 seconds

################# HELPER FUNCS ########################


def get_historical(instId, after='', before='', bar='', limit=''):
    '''
    Self explanatory, basic usage example:

    instId = 'BTC-USD'
    #year, month, day, minute, hour, second
    dt = datetime(2023, 6, 1, 12, 1, 12)
    historical = get_historical(
        instId, after = timestamp(dt), bar = '1m', limit = 10)
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


def get_historical_period(instId, after='', before='', bar='', limit=''):
    '''
    Uses multiple api calls to get historical data over longer period of time

    instId = 'BTC-USD'
    #year, month, day, minute, hour, second
    dt = datetime(2023, 6, 1, 12, 1, 12)
    dt2 = datetime(2023, 6, 2, 12, 1, 12)
    historical = get_historical_period(instId, after=timestamp(
    dt), before=timestamp(dt2), bar='1m', limit=100)

    '''
    # api call is so fucking scuffed, after parameter gets data before that value
    # print(after)
    # print(before)
    after += 6000000
    params = {'instId': instId, 'after': str(
        after), 'before': '', 'bar': bar, 'limit': str(limit)}
    request = make_okx_api_call(
        '/api/v5/market/history-index-candles', params=params)
    new_data = pd.DataFrame(request['data'])
    historical = new_data

    # 6000000ms is the time between each 100 data points
    after += 6000000

    # keep getting data until 'before' time is reached
    while after < before:
        params = {'instId': instId, 'after': str(
            after), 'before': '', 'bar': bar, 'limit': str(limit)}
        request = make_okx_api_call(
            '/api/v5/market/history-index-candles', params=params)
        new_data = pd.DataFrame(request['data'])
        after += 6000000
        historical = pd.concat([historical, new_data], ignore_index=True)

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


def sma_strategy(data, window_size):
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
        if data['Close'].iloc[i] > moving_avg.iloc[i]:
            signals[i] = -1
        elif data['Close'].iloc[i] < moving_avg.iloc[i]:
            signals[i] = 1

    return signals


def get_rsi(deltas, period):
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
    if (avg_downs) == 0:
        avg_downs = 0.1
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

    for i in range(period, len(data)):
        deltas = data['PriceChange'].tolist()[i-period:i]
        rsi = get_rsi(deltas, period)
        if rsi <= buy_thresh:
            signals[i] = 1
        elif rsi >= sell_thresh:
            signals[i] = -1

    return signals


def ema_strategy(data, period):
    signals = np.zeros(len(data))
    ema = data['Close'].ewm(window=period).mean()

    for i in range(period, len(data)):
        if data['Close'].iloc[i] > ema.iloc[i]:
            signals[i] = -1
        elif data['Close'].iloc[i] < ema.iloc[i]:
            signals[i] = 1

    return signals


def get_ema(data, period):
    ema = data['Close'].ewm(span=period).mean()
    return ema


def get_macd(data, short=12, long=26, signal_span=9):
    ema_short = get_ema(data, short)
    ema_long = get_ema(data, long)
    macd = ema_short - ema_long

    macd_signal_line = macd.ewm(span=signal_span).mean()

    return macd, macd_signal_line


def macd_strategy(data, short=12, long=26, signal_span=9):
    macd, macd_signal_line = get_macd(
        data, short=short, long=long, signal_span=signal_span)

    signals = np.zeros(len(data))
    for i in range(long+signal_span, len(data)):
        if macd[i] > macd_signal_line[i]:
            signals[i] = 1
        else:
            signals[i] = -1
    return signals


def neural_network():

    return signals


def simulate_strategy_historical(spot_prices, strategy, initial_balance):
    '''
    Not done
    '''
    pnl = []
    balance = initial_balance
    shares = 0

    match strategy:
        case 'sma':
            signals = sma_strategy(
                spot_prices, window_size=20)
        case 'rsi':
            signals = rsi_strategy(spot_prices, period=14,
                                   buy_thresh=30, sell_thresh=70)
        case'macd':
            signals = macd_strategy(spot_prices)
        case'rsi+macd':
            signals = []
            signals1 = rsi_strategy(spot_prices, period=14,
                                    buy_thresh=30, sell_thresh=70)
            signals2 = macd_strategy(spot_prices)

            i = 0
            for s in signals1:
                if signals1[i] == 1 and signals2[i] == 1:
                    signals.append(1)
                elif signals1[i] == 0 and signals2[i] == 0:
                    signals.append(-1)
                else:
                    signals.append(0)
                i += 1

        case _:
            print("Invalid Strategy")
            return

    assert len(signals) == len(spot_prices)

    for i in range(len(signals)):
        curr_price = int(spot_prices['Close'][i])
        if signals[i] == 1:
            # buy
            bought_shares = balance // curr_price
            shares += bought_shares
            balance -= bought_shares * curr_price
        elif signals[i] == -1:
            # sell
            sold_shares = shares
            balance += sold_shares * curr_price
            shares = 0
        pnl.append(balance+shares*curr_price-initial_balance)

        if balance <= 0:
            print('Bankrupt!')
            break

    return pnl


"""
# Example usage
instId = 'BTC-USD'
dt = datetime(2023, 6, 3, 12, 1, 12)  # year, month, day, minute, hour, second
dt2 = datetime(2023, 6, 6, 12, 1, 12)

data = get_historical(instId, after=timestamp(dt), bar='1m', limit=100)
# visualize_historical(data)
data = data.sort_index()
# print(data)
"""

"""
signals = sma_strategy(data, window_size=5)
print("Trading Signals:", signals)
signals = rsi_strategy(data, period=14, buy_thresh=30, sell_thresh=70)
print("Trading Signals:", signals)
"""

instId = 'BTC-USD'
dt = datetime(2023, 5, 1, 0, 0, 0)  # year, month, day, minute, hour, second
dt2 = datetime(2023, 5, 3, 0, 0, 0)
data = get_historical_period(instId, after=timestamp(
    dt), before=timestamp(dt2), bar='1m', limit=100)
data = data.sort_index()
print(data)

pnl = simulate_strategy_historical(
    spot_prices=data, strategy='rsi+macd', initial_balance=100000)
print(pnl)
