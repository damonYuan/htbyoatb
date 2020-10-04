import os
import backtrader as bt
import quandl
from dotenv import load_dotenv
load_dotenv()
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")
quandl.ApiConfig.api_key = QUANDL_API_KEY


class QuandlDatafeed():
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        df = quandl.get(f'WIKI/{self.code}')
        df = df.rename(index={'Date': 'date'},
                       columns={'Open': 'open',
                              'Close': 'close',
                              'High': 'high',
                              'Low': 'low',
                              'Volume': 'volume'})
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        print(df.head())
        return bt.feeds.PandasData(dataname=df.sort_index(),
                                   fromdate=self.start,
                                   todate=self.end)

    def get_data_default(self):
        return bt.feeds.Quandl(
            dataname=self.code,
            fromdate=self.start,
            todate=self.end,
            buffered=True,
            apikey=QUANDL_API_KEY
        )
