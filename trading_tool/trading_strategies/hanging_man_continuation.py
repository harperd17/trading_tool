import backtrader as bt
import pandas as pd
import numpy as np
from trading_tool.trading_strategies.bracket_strategy import BracketStrategy


def long_criteria(d, params):
  min_top_wick_ratio = params.min_long_wick_ratio
  max_bottom_wick_ratio = params.max_short_wick_ratio
  if isinstance(d,pd.DataFrame):
    d['body_width'] = (d['Close']-d['Open']).abs()
    d['upper_wick'] = d['High'] - d[['Close','Open']].max(axis=1)
    d['lower_wick'] = d[['Close','Open']].min(axis=1) - d['Low']
    d['upper_wick_ratio'] = d['upper_wick']/d['body_width']
    d['lower_wick_ratio'] = d['lower_wick']/d['body_width']
    d['long_upper_wick'] = (d['upper_wick_ratio'] >= min_top_wick_ratio)
    d['short_lower_wick'] = (d['lower_wick_ratio'] <= max_bottom_wick_ratio)
    d = d.replace(np.nan,0)
    d['enter_trade'] = (~(d['body_width']==0)).astype(bool) & (d['long_upper_wick']).astype(bool) & (d['short_lower_wick']).astype(bool)
    return d['enter_trade']
  else:
    body_width = abs(d['Close']-d['Open'])
    if body_width == 0:
      return False
    upper_wick = d['High'] -max(d['Close'],d['Open'])
    lower_wick = min(d['Close'],d['Open']) - d['Low']
    upper_wick_ratio = upper_wick/body_width
    lower_wick_ratio = lower_wick/body_width
    return body_width != 0 and upper_wick_ratio >= min_top_wick_ratio and lower_wick_ratio <= max_bottom_wick_ratio

def short_criteria(d, params):
  min_bottom_wick_ratio = params.min_long_wick_ratio
  max_top_wick_ratio = params.max_short_wick_ratio
  if isinstance(d,pd.DataFrame):
    d['body_width'] = (d['Close']-d['Open']).abs()
    d['upper_wick'] = d['High'] - d[['Close','Open']].max(axis=1)
    d['lower_wick'] = d[['Close','Open']].min(axis=1) - d['Low']
    d['upper_wick_ratio'] = d['upper_wick']/d['body_width']
    d['lower_wick_ratio'] = d['lower_wick']/d['body_width']
    d['short_upper_wick'] = d['upper_wick_ratio'] <= max_top_wick_ratio
    d['long_lower_wick'] = d['lower_wick_ratio'] >= min_bottom_wick_ratio
    d = d.replace(np.nan,0)
    d['enter_trade'] = (~(d['body_width']==0)).astype(bool) & (d['short_upper_wick']).astype(bool) & (d['long_lower_wick']).astype(bool)
    return d['enter_trade']
  else:
    body_width = abs(d['Close']-d['Open'])
    if body_width == 0:
      return False
    upper_wick = d['High'] -max(d['Close'],d['Open'])
    lower_wick = min(d['Close'],d['Open']) - d['Low']
    upper_wick_ratio = upper_wick/body_width
    lower_wick_ratio = lower_wick/body_width
    return body_width != 0 and upper_wick_ratio <= max_top_wick_ratio and lower_wick_ratio >= min_bottom_wick_ratio
  
  
class HangingManContinuationStrategy(BracketStrategy):

    params = (
        ('min_long_wick_ratio',2.0),
        ('max_short_wick_ratio',1.0),
        ('risk_to_reward_ratio',2.0),
        ('fill_ratio',1.5),
    )
    
    indicator_params = {
        'sma_period':21,
        'ema_period':21
    }
    
    indicators = (
    {'params':{'period':indicator_params['sma_period']},'class':MySMA,'name':'sma_'+str(indicator_params['sma_period')},
    {'paras':{'period':indicator_params['ema_period']},'class':MyEMA, 'name':'ema_'+str(indicator_params['ema_period'])},
    )

    def __init__(self):
      super().__init__()
      
    def long_criteria_method(self,data_line):
      return long_criteria(data_line, self.params)
    
    def short_criteria_method(self,data_line):
      return short_criteria(data_line, self.params)
    
    def get_limit_stop_price(self, data_line, direction):
      if direction == 'long':
        limit_price = data_line['Close'] + (data_line['High'] - data_line['Close'])*self.params.fill_ratio
        stop_price = data_line['Close'] - (limit_price-data_line['Close'])*self.params.risk_to_reward_ratio
        return limit_price, stop_price
      elif direction == 'short':
        limit_price = data_line['Close'] - (data_line['Close'] - data_line['Low'])*self.params.fill_ratio
        stop_price = data_line['Close'] + (data_line['Close'] - limit_price)*self.params.risk_to_reward_ratio
        return limit_price, stop_price
    def create_dataframe(self, data):
      for ind in HangingManContinuationStrategy.indicators:
        data[ind['name']] = ind['class'].matrix_method(data, **ind['params'])
      return data
