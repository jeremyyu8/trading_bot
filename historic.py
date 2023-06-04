import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf

from datetime import datetime
 
from main import make_okx_api_call

URL = 'https://www.okx.com'

def get_historical(instId, after = '', before = '', bar = '', limit = ''):
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
 
instId = 'BTC-USD'
dt = datetime(2023, 6, 1, 12, 1, 12) #year, month, day, minute, hour, second
historical = get_historical(instId, after = timestamp(dt), bar = '1m', limit = 10)
visualize_historical(historical)



