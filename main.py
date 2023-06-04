import requests
import pandas as pd

def make_okx_api_call(endpoint, params=None):
    
    base_url = 'https://www.okx.com'
    url = base_url + endpoint

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        raise e
    except ValueError as e:
        raise ValueError('API error: {}'.format(e))

tickers = pd.DataFrame(make_okx_api_call('/api/v5/market/tickers', {'instType': 'SPOT'})['data'])
tickers = tickers.drop('instType', axis=1)
print(tickers)


