import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
from datetime import datetime
import tensorflow as tf

from main import make_okx_api_call

from historic import get_historical_period, timestamp

instId = 'BTC-USD'
dt = datetime(2023, 1, 1, 0, 0, 0)  # year, month, day, minute, hour, second
dt2 = datetime(2023, 6, 1, 0, 0, 0)
data = get_historical_period(instId, after=timestamp(
    dt), before=timestamp(dt2), bar='1m', limit=100)
data = data.sort_index()
print(data.shape[0])
data.to_csv('data.csv')
