import futu as ft
import pandas as pd
import backtrader as bt


class FutuDatafeed():
    def __init__(self, code, start, end):
        self.quote_ctx = None
        self.market = ft.Market.HK
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        ret, df, page_req_key = self.quote_ctx.request_history_kline(self.code,
                                                                     start=self.start,
                                                                     end=self.end,
                                                                     ktype='K_DAY',
                                                                     autype='qfq',
                                                                     max_count=50)
        while page_req_key != None:
            ret, tmp, page_req_key = self.quote_ctx.request_history_kline(self.code,
                                                                          start=self.start,
                                                                          end=self.end,
                                                                          ktype='K_DAY',
                                                                          autype='qfq',
                                                                          max_count=50,
                                                                          page_req_key=page_req_key)

            df = pd.concat([df, tmp])

        df.index = pd.to_datetime(df['time_key'])
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        print(df)
        return bt.feeds.PandasData(dataname=df.sort_index(),
                                   fromdate=pd.to_datetime(self.start),
                                   todate=pd.to_datetime(self.end))

    def __enter__(self):
        self.quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)
        self.quote_ctx.start()
        self.quote_ctx.set_handler(ft.TickerHandlerBase())
        return self

    def __exit__(self, *args):
        ret, data = self.quote_ctx.get_history_kl_quota(get_detail=True)
        if ret == ft.RET_OK:
            print(data)
        else:
            print('error:', data)
        self.quote_ctx.stop()
        self.quote_ctx.close()