import backtrader as bt
from abc import ABC, abstractmethod
 


class BracketStrategy(bt.Strategy):
    entries = ()
    limits = ()
    stops = ()
    bar_openings = ()
    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.current_bar = 1
        
    @abstractmethod
    def long_criteria(data_line, params):
      ...
      
    @abstractmethod
    def short_criteria(data_line, params):
      ...
      
    @abstractmethod
    def get_limit_stop_price(data_line, direction, params):
      ...
      
    @abstractmethod
    def next(self):
      data_line = pd.Series([self.data_close[0],self.data_open[0],self.data_high[0],self.data_low[0]], index = ['Close','Open','High','Low'])
      if long_criteria(data_line, self.params):
          # enter long bracket
          limit_price, stop_price = self.get_limit_stop_price(data_line, 'long', self.params)
          bracket_buy = self.buy_bracket(limitprice=limit_price, stopprice=stop_price)
          # record the trade prices
          self.limits.append(limit_price)
          self.stops.append(stop_price)
          self.bar_openings.append(self.current_bar)

      elif short_criteria(data_line, self.params):
          # enter short bracket
          limit_price, stop_price = self.get_limit_stop_price(data_line, 'short', self.params)
          bracket_sell = self.sell_bracket(limitprice=limit_price, stopprice=stop_price)
          # record the trade prices
          self.limits.append(limit_price)
          self.stops.append(stop_price)
          self.bar_openings.append(self.current_bar)
      self.current_bar += 1