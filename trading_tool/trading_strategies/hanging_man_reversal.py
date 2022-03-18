import backtrader as bt
import pandas as pd
from trading_tool.trading_strategies.bracket_strategy import BracketStrategy
from trading_tool.trading_strategies.hanging_man_continuation import long_criteria, short_criteria


  
class HangingManReversalStrategy(BracketStrategy):

    params = (
        ('min_long_wick_ratio',2.0),
        ('max_short_wick_ratio',1.0),
        ('risk_to_reward_ratio',2.0),
        ('fill_ratio',1.5)
    )

    def __init__(self):
      super().__init__()
      
    def long_criteria_method(self,data_line):
      return short_criteria(data_line, self.params)
    
    def short_criteria_method(self,data_line):
      return long_criteria(data_line, self.params)
    
    def get_limit_stop_price(self, data_line, direction, params):
      if direction == 'long':
        limit_price = data_line['Close'] + (data_line['Close'] - data_line['Low'])*self.params.fill_ratio
        stop_price = data_line['Close'] - (limit_price - data_line['Close'])*self.params.risk_to_reward_ratio
      elif direction == 'short':
        limit_price = data_line['Close'] - (data_line['High'] - data_line['Close'])*self.params.fill_ratio
        stop_price = data_line['Close'] + (data_line['Close'] - limit_price)*self.params.risk_to_reward_ratio
