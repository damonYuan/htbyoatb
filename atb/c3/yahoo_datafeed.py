from pandas_datareader import data
import backtrader as bt


class YahooDatafeed():
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        df = data.DataReader(self.code,
                               start=self.start,
                               end=self.start,
                               data_source='yahoo')
        df = df.rename(index={'Date': 'date'},
                       columns={'Open': 'open',
                                'Adj Close': 'close',
                                'High': 'high',
                                'Low': 'low',
                                'Volume': 'volume'})
        df['openinterest'] = 0
        print(df.head())
        return bt.feeds.PandasData(dataname=df.sort_index(),
                                   fromdate=self.start,
                                   todate=self.end)
