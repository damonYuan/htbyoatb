import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from atb.c3.tushare_datafeed import TushareDatafeed
from atb.c3.quandl_datafeed import QuandlDatafeed
from atb.c3.futu_datafeed import FutuDatafeed
from atb.c3.gold import Gold
from datetime import datetime


def main():
    cmd = input("enter command: ")
    cmd_list = cmd.split(',')
    if cmd_list[0] == 'c3':
        if cmd_list[1] == 'tushare':
            feed = TushareDatafeed(code='600000.SH',
                                   start='20190331',
                                   end='20200331').get_data()
            print(feed)
        elif cmd_list[1] == 'quandl':
            feed = QuandlDatafeed(code='AAPL',
                                  start=datetime(2017, 1, 1),
                                  end=datetime(2018, 1, 1)).get_data()
            print(feed)
        elif cmd_list[1] == 'futu':
            with FutuDatafeed(code='HK.00124', start='2018-01-01', end='2019-01-01') as f:
                feed = f.get_data()
            print(feed)
        elif cmd_list[1] == 'gold':
            gold = Gold()
            gold.collect()
    elif cmd_list[0] == 'quit':
        exit(0)



if __name__ == '__main__':
    main()
