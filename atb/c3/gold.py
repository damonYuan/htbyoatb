import backtrader as bt
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")


class Gold:
    def __init__(self):
        self.gld_code = 'GLD'
        self.gdx_code = 'GDX'
        self.start = pd.to_datetime('20100331')
        self.end = pd.to_datetime('20200331')
        self.gld = None
        self.ddx = None

    def collect(self):
        '''
        收集数据
        :return: Quandl datafeed
        '''
        self.gld = bt.feeds.Quandl(
            dataname=self.gld_code,
            fromdate=self.start,
            todate=self.end,
            buffered=True,
            apikey=QUANDL_API_KEY
        )
        self.gdx = bt.feeds.Quandl(
            dataname=self.gdx_code,
            fromdate=self.start,
            todate=self.end,
            buffered=True,
            apikey=QUANDL_API_KEY
        )
        print(self.gld)
        print(self.gdx)

    def prepare(self):
        '''
        该数据已经
        - 前复权
        - 有最高最低价及必要数据
          ['open', 'high', 'low', 'close', 'volume', 'openinterest']
        - 已经选好股票对象，不存在幸存者偏差问题
        :return: Quandl datafeed
        '''
        return

    def analyze(self):
        '''

        :return: backtrader strategy
        '''
        class GoldStrategy(bt.Strategy):
            def __init__(self):
                self.orderid = None

            def next(self):
                print(self.data0[0])
                print(self.data1[0])

        return GoldStrategy

    def train(self):
        cerebro = bt.Cerebro()
        self.collect()
        self.prepare()
        cerebro.adddata(self.gld)
        cerebro.adddata(self.gdx)
        cerebro.addstrategy(self.analyze)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        cerebro.broker.setcash(10000)
        cerebro.broker.setcommission(commission=0.002)
        cerebro.addsizer(bt.sizers.FixedSize, stake=500)
        results = cerebro.run(maxcpus=1)
        strat = results[0]
        print('夏普比率:', strat.analyzers.SharpeRatio.get_analysis())
        print('回撤指标:', strat.analyzers.DW.get_analysis())

    def test(self):
        '''

        :return:
        '''
        pass

    def use(self):
        pass