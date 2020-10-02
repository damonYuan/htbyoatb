import tushare as ts
import pandas as pd
import backtrader as bt


class TushareDatafeed:
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        df = ts.pro_bar(ts_code=self.code,
                        adj='qfq',
                        start_date=self.start,
                        end_date=self.end)
        df['date'] = df['trade_date']
        df['volume'] = df['vol']
        df.index = pd.to_datetime(df['date'])
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        print(df)
        return bt.feeds.PandasData(dataname=df.sort_index(),
                                         fromdate=pd.to_datetime(self.start),
                                         todate=pd.to_datetime(self.end))
