import backtrader as bt
import talib

class SMA(bt.Indicator):
    lines = ('sma',)

    params = (('period', 15),)

    def __init__(self):
        self.lines.sma = bt.talib.SMA(self.data, period=self.p.period)

    def matrix_method(data, period):
      # this method isn't actually meant to be used by this class, but just to be able to link the method
      # for calculating the indicator
        return talib.SMA(data['Close'],timeperiod=period)
      
      
class EMA(bt.Indicator):
    lines = ('ema',)

    params = (('period', 15),)

    def __init__(self):
        self.lines.ema = bt.talib.EMA(self.data, period=self.p.period)

    def matrix_method(data, period):
      # this method isn't actually meant to be used by this class, but just to be able to link the method
      # for calculating the indicator
        return talib.EMA(data['Close'],timeperiod=period)
