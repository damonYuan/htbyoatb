import pandas as pd
import datetime
import yfinance as yf
import os
import pandas as pd
from pandas_datareader import data as pdr


class MeanRevert:
    def __init__(self):
        pass

    def collect(self):
        yf.pdr_override()
        payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = payload[0]
        tickers = df['Symbol'].unique().tolist()
        pd.Series(tickers).to_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'tickers.csv'))
        if not os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')):
            os.makedirs(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data'))
        for t in tickers:
            try:
                print(t)
                df = pdr.get_data_yahoo(t, start="2000-01-01", end="2020-10-06")
                df.to_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', f'{t}.csv'))
            except Exception as e:
                print(e)

    def prepare(self):
        pass
