from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from pandas_datareader import data
import matplotlib.pyplot as plt


class PairTradingStrategy(bt.Strategy):
    params = dict(
        period=10,
        stake=10,
        qty1=0,
        qty2=0,
        printout=True,
        upper=2.1,
        lower=-2.1,
        up_medium=1,
        low_medium=-1,
        status=0,
        portfolio_value=10000,
    )

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            self.log('order status - %s ,' % order.Status[order.status])
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None

    def __init__(self):
        # To control operation entries
        self.orderid = None
        self.qty1 = self.p.qty1
        self.qty2 = self.p.qty2
        self.upper_limit = self.p.upper
        self.lower_limit = self.p.lower
        self.up_medium = self.p.up_medium
        self.low_medium = self.p.low_medium
        self.status = self.p.status
        self.portfolio_value = self.p.portfolio_value

        # Signals performed with PD.OLS :
        self.transform = btind.OLS_TransformationN(self.data0, self.data1,
                                                   period=self.p.period)
        self.zscore = self.transform.zscore

        # Checking signals built with StatsModel.API :
        # self.ols_transfo = btind.OLS_Transformation(self.data0, self.data1,
        #                                             period=self.p.period,
        #                                             plot=True)

    def next(self):

        if self.orderid:
            return  # if an order is active, no new orders are allowed

        if self.p.printout:
            # print('Self  len:', len(self))
            # print('Data0 len:', len(self.data0))
            # print('Data1 len:', len(self.data1))
            print('Data0 len == Data1 len:',
                  len(self.data0) == len(self.data1))

            print('Data0 dt:', self.data0.datetime.datetime())
            print('Data1 dt:', self.data1.datetime.datetime())

        print('status is', self.status)
        print('zscore is', self.zscore[0])

        # Step 2: Check conditions for SHORT & place the order
        # Checking the condition for SHORT
        if (self.zscore[0] > self.upper_limit) and (self.status != 1):

            # Calculating the number of shares for each stock
            value = 0.5 * self.portfolio_value  # Divide the cash equally
            x = int(value / (self.data0.close))  # Find the number of shares for Stock1
            y = int(value / (self.data1.close))  # Find the number of shares for Stock2
            print('x + self.qty1 is', x + self.qty1)
            print('y + self.qty2 is', y + self.qty2)

            # Placing the order
            self.log('SELL CREATE %s, price = %.2f, qty = %d' % ("PEP", self.data0.close[0], x + self.qty1))
            self.sell(data=self.data0, size=(x + self.qty1))  # Place an order for buying y + qty2 shares
            self.log('BUY CREATE %s, price = %.2f, qty = %d' % ("KO", self.data1.close[0], y + self.qty2))
            self.buy(data=self.data1, size=(y + self.qty2))  # Place an order for selling x + qty1 shares

            # Updating the counters with new value
            self.qty1 = x  # The new open position quantity for Stock1 is x shares
            self.qty2 = y  # The new open position quantity for Stock2 is y shares

            self.status = 1  # The current status is "short the spread"

            # Step 3: Check conditions for LONG & place the order
            # Checking the condition for LONG
        elif (self.zscore[0] < self.lower_limit) and (self.status != 2):

            # Calculating the number of shares for each stock
            value = 0.5 * self.portfolio_value  # Divide the cash equally
            x = int(value / (self.data0.close))  # Find the number of shares for Stock1
            y = int(value / (self.data1.close))  # Find the number of shares for Stock2
            print('x + self.qty1 is', x + self.qty1)
            print('y + self.qty2 is', y + self.qty2)

            # Place the order
            self.log('BUY CREATE %s, price = %.2f, qty = %d' % ("PEP", self.data0.close[0], x + self.qty1))
            self.buy(data=self.data0, size=(x + self.qty1))  # Place an order for buying x + qty1 shares
            self.log('SELL CREATE %s, price = %.2f, qty = %d' % ("KO", self.data1.close[0], y + self.qty2))
            self.sell(data=self.data1, size=(y + self.qty2))  # Place an order for selling y + qty2 shares

            # Updating the counters with new value
            self.qty1 = x  # The new open position quantity for Stock1 is x shares
            self.qty2 = y  # The new open position quantity for Stock2 is y shares
            self.status = 2  # The current status is "long the spread"


            # Step 4: Check conditions for No Trade
            # If the z-score is within the two bounds, close all
        elif (self.zscore[0] < self.up_medium and self.zscore[0] > self.low_medium) and (self.status != 0):
            self.log('CLOSE LONG %s, price = %.2f' % ("PEP", self.data0.close[0]))
            self.close(self.data0)
            self.log('CLOSE LONG %s, price = %.2f' % ("KO", self.data1.close[0]))
            self.close(self.data1)
            self.status = 0
        else:
            self.log(f'haha -  {self.status}')

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')


def runstrategy():
    # Create a cerebro
    cerebro = bt.Cerebro()

    # Get the dates from the args
    sfromdate = '2020-05-01'
    stodate = datetime.date(datetime.now())
    fromdate = datetime.strptime(sfromdate, '%Y-%m-%d')
    todate = datetime.now()

    gld = data.DataReader('GLD',
                          start=sfromdate,
                          end=stodate,
                          data_source='yahoo')
    gld = gld.drop(columns=['Close'])
    gld = gld.rename(index={'Date': 'date'},
                     columns={'Open': 'open',
                              'Adj Close': 'close',
                              'High': 'high',
                              'Low': 'low',
                              'Volume': 'volume'})

    gdx = data.DataReader('GDX',
                          start=sfromdate,
                          end=stodate,
                          data_source='yahoo')
    gdx = gdx.drop(columns=['Close'])
    gdx = gdx.rename(index={'Date': 'date'},
                     columns={'Open': 'open',
                              'Adj Close': 'close',
                              'High': 'high',
                              'Low': 'low',
                              'Volume': 'volume'})


    # Add the 1st data to cerebro
    cerebro.adddata(bt.feeds.PandasData(dataname=gld.sort_index(),
                                        fromdate=fromdate,
                                        todate=todate), name='gld')

    # Add the 2nd data to cerebro
    cerebro.adddata(bt.feeds.PandasData(dataname=gdx.sort_index(),
                                        fromdate=fromdate,
                                        todate=todate), name='gdx')

    # Add the strategy
    cerebro.addstrategy(PairTradingStrategy,
                        period=60,
                        stake=10)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(100000)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcommission(commission=0.03)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio', riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='Returns')

    # And run it
    results = cerebro.run(runonce=False, # https://community.backtrader.com/topic/242/is-backtrader-event-driven-or-vectorized/2
                preload=False,
                oldsync=True)

    strat = results[0]
    print('夏普比率:', strat.analyzers.SharpeRatio.get_analysis())
    print('回撤指标:', strat.analyzers.DW.get_analysis())
    print('回报:', strat.analyzers.Returns.get_analysis())

    # Plot if requested
    # cerebro.plot(numfigs=1, volume=False, zdown=False)

