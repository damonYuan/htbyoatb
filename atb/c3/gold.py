import backtrader as bt
import pandas as pd
from pandas_datareader import data
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class Gold:
    def __init__(self):
        self.gld_code = 'GLD'
        self.gdx_code = 'GDX'
        self.start = '2006-01-21'
        self.end = '2009-12-21'
        self.gld = None
        self.gld_train = None
        self.gld_test = None
        self.gdx = None
        self.gdx_train = None
        self.gdx_test = None
        self.train_hedge_ration = None
        self.test_hedge_ration = None

    def collect(self):
        df = data.DataReader(self.gld_code,
                               start=self.start,
                               end=self.end,
                               data_source='yahoo')
        df = df.drop(columns=['Close'])
        self.gld = df.rename(index={'Date': 'date'},
                       columns={'Open': 'open',
                                'Adj Close': 'close',
                                'High': 'high',
                                'Low': 'low',
                                'Volume': 'volume'})
        # print(self.gld.head())
        df = data.DataReader(self.gdx_code,
                             start=self.start,
                             end=self.end,
                             data_source='yahoo')
        df = df.drop(columns=['Close'])
        self.gdx = df.rename(index={'Date': 'date'},
                             columns={'Open': 'open',
                                      'Adj Close': 'close',
                                      'High': 'high',
                                      'Low': 'low',
                                      'Volume': 'volume'})
        # print(self.gdx.head())

    def prepare(self):
        '''
        该数据已经
        - 前复权
        - 有最高最低价及必要数据
          ['open', 'high', 'low', 'close', 'volume', 'openinterest']
        - 已经选好股票对象，不存在幸存者偏差问题
        但是需要
        - 找到两只股票交易日的交集
        - 交易日期按照升序排序
        - 添加 df['openinterest'] = 0，这个数据列是 backtrader 所需要的，我会另开
          一篇博客学习一下这个参数的意义
        - 将数据平均分为两部分，上半部分作为训练数据，下半部分作为测试数据
        '''
        intersection = self.gld.index.intersection(self.gdx.index)
        self.gld = self.gld.loc[intersection]
        self.gld = self.gld.sort_index()
        self.gld['openinterest'] = 0
        print(self.gld.head())
        self.gdx = self.gdx.loc[intersection]
        self.gdx = self.gdx.sort_index()
        self.gdx['openinterest'] = 0
        print(self.gdx.head())

        s = self.gld.index.size // 2
        self.gld_train = self.gld[:s]
        self.gld_test = self.gld[s:]
        self.gdx_train = self.gdx[:s]
        self.gdx_test = self.gdx[s:]

    def analyze(self):
        # train linear regression and beta weight
        train_feature = self.gdx_train['close']
        train_target = self.gld_train['close']
        train_feature = sm.add_constant(train_feature, prepend=False)
        train_model = sm.OLS(train_target, train_feature).fit()
        train_predictions = train_model.predict(train_feature)
        # print(train_model.summary())

        train_hedge_ratio = train_model.params['close']
        print(train_hedge_ratio)
        train_spread = train_target - train_hedge_ratio*train_feature['close']
        train_spread_mean = train_spread.mean()
        train_spread_std = train_spread.std()

        # test = (train_spread - train_spread_mean) / train_spread_std
        # test.plot()
        # plt.show()

        # test linear regression and beta weight
        # test_feature = self.gld_test['close']
        # test_target = self.gdx_test['close']
        # test_model = sm.OLS(test_target, test_feature).fit()
        # test_predictions = test_model.predict(test_feature)
        # print(test_model.summary())

        # draw the diagram
        # plt.scatter(train_feature['close'], train_target, color='black', s=1)
        # plt.plot(train_feature['close'], train_predictions, color='blue', linewidth=3)
        # plt.xticks(())
        # plt.yticks(())
        # plt.xlabel('GDX')
        # plt.ylabel('GLD')
        # plt.show()

        class GoldStrategy(bt.Strategy):
            params = (('longs', -2),('shorts', 2),('exits', 1),('portfolio_value', 10000))

            def __init__(self):
                self.buy_order = None
                self.sell_order = None
                self.gldclose = self.datas[0].close
                self.gdxclose = self.datas[1].close
                self.longs = self.params.longs

            def log(self, txt, dt=None):
                """
                Logging function for this strategy
                """
                dt = dt or self.datas[0].datetime.date(0)
                print('%s, %s' % (dt.isoformat(), txt))

            def next(self):
                spread = self.gldclose[0] - train_hedge_ratio*self.gdxclose[0]
                zscore = (spread - train_spread_mean) / train_spread_std
                if self.buy_order and self.sell_order:
                    if abs(zscore) <= self.p.exits:
                        self.log(
                            'close the spread - gld close %.2f and gdx close %.2f' % (self.gldclose[0], self.gdxclose[0]))
                        self.close(self.datas[0])
                        self.close(self.datas[1])
                        self.buy_order = None
                        self.sell_order = None
                    return

                if zscore <= self.p.longs:
                    self.log(
                        'buy the spread - gld close %.2f and gdx close %.2f' % (self.gldclose[0], self.gdxclose[0]))
                    sell_size = int(self.params.portfolio_value * 0.5 / self.gdxclose[0])
                    buy_size = int(self.params.portfolio_value * 0.5 / self.gldclose[0])
                    self.sell_order = self.sell(data=self.datas[1], size=sell_size)
                    self.buy_order = self.buy(data=self.datas[0], size=buy_size)
                elif zscore >= self.p.shorts:
                    self.log(
                        'sell the spread - gld close %.2f and gdx close %.2f' % (self.gldclose[0], self.gdxclose[0]))
                    sell_size = int(self.params.portfolio_value * 0.5 / self.gldclose[0])
                    buy_size = int(self.params.portfolio_value * 0.5 / self.gdxclose[0])
                    self.sell_order = self.sell(data=self.datas[0], size=sell_size)
                    self.buy_order = self.buy(data=self.datas[1], size=buy_size)
                else:
                    return

            def stop(self):
                self.log('Ending Value %.2f' % self.broker.getvalue())

        return GoldStrategy

    def train(self):
        cerebro = bt.Cerebro()
        self.collect()
        self.prepare()
        cerebro.adddata(bt.feeds.PandasData(dataname=self.gld_train.sort_index(),
                                   fromdate=pd.to_datetime(self.start),
                                   todate=pd.to_datetime(self.end)), name='gld')
        cerebro.adddata(bt.feeds.PandasData(dataname=self.gdx_train.sort_index(),
                                   fromdate=pd.to_datetime(self.start),
                                   todate=pd.to_datetime(self.end)), name='gdx')
        cerebro.addstrategy(self.analyze())
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
        cerebro.broker.setcash(100)
        cerebro.broker.setcommission(commission=0)
        cerebro.addsizer(bt.sizers.FixedSize, stake=500)
        results = cerebro.run(maxcpus=1)
        strat = results[0]
        print('夏普比率:', strat.analyzers.SharpeRatio.get_analysis())
        print('回撤指标:', strat.analyzers.DW.get_analysis())

        # plt.rcParams['font.sans-serif'] = ['SimHei']
        # plt.rcParams['axes.unicode_minus'] = False
        # plt.rcParams['figure.figsize'] = [9, 8]
        # plt.rcParams['figure.dpi'] = 125
        # plt.rcParams['figure.facecolor'] = 'w'
        # plt.rcParams['figure.edgecolor'] = 'k'
        # cerebro.plot(iplot=False)

    def test(self):
        '''

        :return:
        '''
        pass

    def use(self):
        pass