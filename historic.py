import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
from datetime import datetime
import tensorflow as tf
import threading

from main import make_okx_api_call

# api limit is 20 requests/2 seconds


class BackTester:
    def __init__(self, symbol):
        self.symbol = symbol
        self.signals = []
        self.data = None

    ########################################## FETCH DATA ##########################################
    def fetch_data_csv(self, filename='data.csv'):
        print("Fetching data from csv....")
        self.data = pd.read_csv(filename)

    def fetch_data_api(self, after='', before='', bar='', limit=''):
        '''
        Uses multiple api calls to get historical data over longer period of time

        instId = 'BTC-USD'
        #year, month, day, minute, hour, second
        dt = datetime(2023, 6, 1, 12, 1, 12)
        dt2 = datetime(2023, 6, 2, 12, 1, 12)
        historical = get_historical_period(instId, after=timestamp(
        dt), before=timestamp(dt2), bar='1m', limit=100)

        '''
        print("Fetching data from API....")

        # api call is so fucking scuffed, after parameter gets data before that value
        after += 6000000
        params = {'instId': self.symbol, 'after': str(
            after), 'before': '', 'bar': bar, 'limit': str(limit)}
        request = make_okx_api_call(
            '/api/v5/market/history-index-candles', params=params)
        new_data = pd.DataFrame(request['data'])
        historical = new_data

        # 6000000ms is the time between each 100 data points
        after += 6000000

        # keep getting data until 'before' time is reached
        while after < before:
            params = {'instId': self.symbol, 'after': str(
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
        historical = historical.sort_index()

        self.data = historical
        print("Completed API data fetch")

    def visualize_historical(self):
        mpf.plot(self.data, type='candle', title='Candlestick Chart')

    ########################################## SMA STRATEGY ##########################################
    def sma_strategy(self, window_size):
        print("Generating SMA signals....")
        """
        Implements a simple moving average strategy using candlestick data.

        Parameters:
        - data: A DataFrame containing candlestick data with columns 'open', 'high', 'low', and 'close'.
        - window_size: The size of the moving average window.

        Returns:
        - An array of signals (1 for buy, -1 for sell, 0 for hold).
        """
        data = self.data
        signals = np.zeros(len(data))
        moving_avg = data['Close'].rolling(window=window_size).mean()

        for i in range(window_size, len(data)):
            if data['Close'].iloc[i] > moving_avg.iloc[i]:
                signals[i] = -1
            elif data['Close'].iloc[i] < moving_avg.iloc[i]:
                signals[i] = 1

        self.signals.append(signals)

    ########################################## RSI STRATEGY ##########################################
    def get_rsi(self, deltas, period):
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

    def rsi_strategy(self, period=14, buy_thresh=30, sell_thresh=70):
        '''
        Implements a simple relative strength index strategy using candlestick data.
        >=sell_thresh -> sell, <=buy_thresh -> buy

        Parameters:
        - data: A DataFrame containing candlestick data with columns 'open', 'high', 'low', and 'close'.
        - period: Number of most recent close prices used in rsi calculation

        Returns:
        - An array of signals (1 for buy, -1 for sell, 0 for hold).

        '''
        print("Generating RSI signals....")

        data = self.data
        signals = np.zeros(len(data))

        # get deltas
        data['PriceChange'] = data['Close'].diff().fillna(0).round(2)

        for i in range(period, len(data)):
            deltas = data['PriceChange'].tolist()[i-period:i]
            rsi = self.get_rsi(deltas, period)
            if rsi <= buy_thresh:
                signals[i] = 1
            elif rsi >= sell_thresh:
                signals[i] = -1

        self.signals.append(signals)

    ########################################## EMA STRATEGY ##########################################
    def ema_strategy(self, period=20):
        print("Generating EMA signals....")

        data = self.data
        signals = np.zeros(len(data))
        ema = data['Close'].ewm(window=period).mean()

        for i in range(period, len(data)):
            if data['Close'].iloc[i] > ema.iloc[i]:
                signals[i] = -1
            elif data['Close'].iloc[i] < ema.iloc[i]:
                signals[i] = 1

        self.signals.append(signals)

    ########################################## MACD STRATEGY ##########################################
    def get_macd(self, short=12, long=26, signal_span=9):
        data = self.data
        ema_short = data['Close'].ewm(span=short).mean()
        ema_long = data['Close'].ewm(span=long).mean()
        macd = ema_short - ema_long

        macd_signal_line = macd.ewm(span=signal_span).mean()

        return macd, macd_signal_line

    def macd_strategy(self, short=12, long=26, signal_span=9):
        print("Generating MACD signals....")
        data = self.data
        macd, macd_signal_line = self.get_macd(
            short=short, long=long, signal_span=signal_span)

        signals = np.zeros(len(data))
        for i in range(long+signal_span, len(data)):
            if macd[i] > macd_signal_line[i]:
                signals[i] = 1
            else:
                signals[i] = -1

        self.signals.append(signals)

    ########################################## SIGNAL PROCESSING ##########################################

    def combine_signals(self):
        print("Combining signals....")
        combined_signals = []
        signals = self.signals
        for j in range(len(signals[0])):
            for i in range(len(signals)):
                buy = True
                sell = True
                if signals[i][j] != 1:
                    buy = False
                if signals[i][j] != -1:
                    sell = False
            if buy:
                combined_signals.append(1)
            elif sell:
                combined_signals.append(-1)
            else:
                combined_signals.append(0)
        self.signals = combined_signals

    def reset_signals(self):
        self.signals = []

    ########################################## SIMULATE ##########################################

    def simulate_strategy(self, initial_balance=100000):
        print("Running simulation....")
        if len(self.signals) == 0:
            print("Please run a strategy first to generate signals")
            return

        signals = self.signals
        spot_prices = self.data
        pnl = []
        balance = initial_balance
        shares = 0

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

            if balance < 0:
                print('Bankrupt!')
                print(curr_price, bought_shares, sold_shares, balance)
                break

        self.pnl = pnl

    def show_cumulative_pnl(self):
        print("Total profit/loss after simulation:", self.pnl[-1])


"""
Sample usage of BackTest
"""
# helper function for converting datetime


def timestamp(dt):
    epoch = datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000)


dt = datetime(2023, 5, 1, 0, 0, 0)  # year, month, day, minute, hour, second
dt2 = datetime(2023, 5, 2, 0, 0, 0)

back_tester = BackTester('BTC-USD')

# x = threading.Thread(target=back_tester.fetch_data_api,
#                      args=(timestamp(dt), timestamp(dt2), '1m', 100,))
# x.start()
# back_tester.fetch_data_api(after=timestamp(
#     dt), before=timestamp(dt2), bar='1m', limit=100)
back_tester.fetch_data_csv()
back_tester.macd_strategy()
back_tester.rsi_strategy()
back_tester.combine_signals()
back_tester.simulate_strategy()
back_tester.show_cumulative_pnl()
