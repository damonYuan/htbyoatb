import os
import backtrader as bt
from dotenv import load_dotenv
load_dotenv()
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")

class QuandlDatafeed():
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end

    def get_data(self):
        return bt.feeds.Quandl(
            dataname=self.code,
            fromdate=self.start,
            todate=self.end,
            buffered=True,
            apikey=QUANDL_API_KEY
        )
