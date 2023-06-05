import requests
import pandas as pd

from main import make_okx_api_call

##################### HELPER FUNCTIONS FOR LIVE DATA #######################################

def get_spot_price(symbol):
    '''
    Get the spot price for a given symbol, returns the price as a float
    '''    

    params = {'instId': symbol}
    response = make_okx_api_call('/api/v5/market/ticker', params)
    #print(response)
    spot_price = float(response['data'][0]['last'])
    return spot_price

###############################################################################################

def basic_moving_average_strategy(symbol, threshold = 0.05):
    '''
    Returns "Buy", "Sell", or "None"
    '''

    spot_price = get_spot_price(symbol)
    pass



def simulate_strategy_live(symbol, strategy, initial_balance, freq):
    pass

print(get_spot_price('MDT-USDT'))