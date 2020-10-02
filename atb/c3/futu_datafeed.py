import futu as ft


class FutuDatafeed():
    def __init__(self, code, start=None, end=None):
        self.quote_ctx = None
        self.market = ft.Market.HK
        self.code = code
        self.start = '2018-01-01'
        self.end = '2019-01-01'
        self.code_list = [self.code]

    def get_data(self):
        # print(self.quote_ctx.get_trading_days(self.market, start=self.start, end=self.end))  # 获取交易日
        # print(self.quote_ctx.get_stock_basicinfo(self.market, stock_type=ft.SecurityType.STOCK))  # 获取股票信息
        ret, df, page_req_key = self.quote_ctx.request_history_kline(self.code,
                                         start=self.start,
                                         end=self.end,
                                         ktype='K_DAY',
                                         autype='qfq',
                                                                     max_count=50)  # 获取历史K线
        print(df)
        df['openinterest'] = 0
        df = df[['open', 'high', 'low', 'close', 'volume', 'openinterest']]
        return df

    def get_rt_data(self):
        self.fquote_ctx.subscribe(self.code, [ft.SubType.QUOTE, ft.SubType.TICKER, ft.SubType.K_DAY, ft.SubType.ORDER_BOOK,
                                   ft.SubType.RT_DATA, ft.SubType.BROKER])
        print(self.quote_ctx.get_stock_quote(self.code))  # 获取报价
        print(self.quote_ctx.get_rt_ticker(self.code))  # 获取逐笔
        print(self.quote_ctx.get_cur_kline(self.code, num=100, ktype=ft.KLType.K_DAY))  # 获取当前K线
        print(self.quote_ctx.get_order_book(self.code))  # 获取摆盘
        print(self.quote_ctx.get_rt_data(self.code))  # 获取分时数据
        print(self.quote_ctx.get_broker_queue(self.code))  # 获取经纪队列

    def __enter__(self):
        self.quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)
        self.quote_ctx.start()
        self.quote_ctx.set_handler(ft.TickerHandlerBase())
        return self

    def __exit__(self, *args):
        self.quote_ctx.stop()
        self.quote_ctx.close()