#GET /api/v5/market/history-index-candles
# GET /api/v5/market/index-candles?instId=BTC-USD

import requests
import pandas as pd

# get tickers
url = 'https://www.okx.com'
tickers = pd.DataFrame(
    (requests.get(url+'/api/v5/market/tickers?instType=SPOT').json())['data'])
tickers = tickers.drop('instType', axis=1)
print(tickers)

# get historic candlesticks for btc-usd
instId = 'BTC-USD'
after = ''
before = ''
bar = ''
limit = ''
request = '/api/v5/market/history-index-candles?instId=' + instId

historical = pd.DataFrame((requests.get(
    url+request).json())['data'])
historical.columns = ["Date", "Open", "High", "Low", "Close", "State"]
historical['Date'] = pd.to_datetime(historical['Date'], unit='ms')
historical.set_index('Date', inplace=True)
historical.sort_values(by='Date')
print(historical)
