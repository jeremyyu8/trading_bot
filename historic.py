import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np 
from datetime import datetime
 
from main import make_okx_api_call

################# HELPER FUNCS ########################

def get_historical(instId, after = '', before = '', bar = '', limit = ''):

    '''
    Self explanatory, basic usage example:

    instId = 'BTC-USD'
    dt = datetime(2023, 6, 1, 12, 1, 12) #year, month, day, minute, hour, second
    historical = get_historical(instId, after = timestamp(dt), bar = '1m', limit = 10)
    visualize_historical(historical)
    
    '''

    params = {'instId': instId, 'after': str(after), 'before': str(before), 'bar': bar, 'limit': str(limit)}
    request = make_okx_api_call('/api/v5/market/history-index-candles', params=params)
    
    historical = pd.DataFrame(request['data'])

    historical.columns = ["Date", "Open", "High", "Low", "Close", "State"]
    historical = historical.drop('State', axis = 1)
    historical['Date'] = pd.to_datetime(historical['Date'], unit='ms')

    #cast to floats lol
    historical['Open'] = historical['Open'].astype(float)
    historical['High'] = historical['High'].astype(float)
    historical['Low'] = historical['Low'].astype(float)
    historical['Close'] = historical['Close'].astype(float)

    historical.set_index('Date', inplace=True)
    historical.sort_values(by='Date')
    return historical

def visualize_historical(data):
    mpf.plot(data, type = 'candle', title = 'Candlestick Chart')

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
            signals[i] = 1  
        elif data['Close'].iloc[i] < moving_avg.iloc[i - window_size]:  
            signals[i] = -1  

    return signals

def calculate_rsi(prices, period):
    '''
    Calculate Relative Strength Index (0-100); >70 -> sell, <=30 -> buy
    '''
    pass

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
    spot_prices = get_historical(symbol, start_date, end_date) #fix

    signals = strategy(spot_prices)

    assert len(signals) == len(spot_prices)

    for i in range(len(signals)):
        
        if signals[i] == 1:
            balance -= spot_prices[i]
        elif signals[i] == -1:
            balance += spot_prices[i]
        
        pnl.append(balance)

        if balance <= 0:
            print('Bankrupt!')
            break 

    return pnl

# Example usage
instId = 'BTC-USD'
dt = datetime(2023, 6, 1, 12, 1, 12) #year, month, day, minute, hour, second
data = get_historical(instId, after = timestamp(dt), bar = '1m', limit = 100)
visualize_historical(data)

signals = moving_average_strategy_candles(data, window_size = 5)
print("Trading Signals:", signals)

