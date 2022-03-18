import backtrader as bt
import pandas as pd


def long_criteria(d, min_top_wick_ratio, max_bottom_wick_ratio):
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

  


def short_criteria(d, min_bottom_wick_ratio, max_top_wick_ratio):
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
  
  
class HangingManContinuationStrategy(bt.Strategy):

    params = (
        ('min_long_wick_ratio',2.0),
        ('max_short_wick_ratio',1.0),
        ('risk_to_reward_ratio',2.0),
        ('fill_ratio',1.5)
    )

    def __init__(self):#, min_long_wick_ratio, max_short_wick_ratio, risk_to_reward_ratio):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low

        self.entries = []
        self.limits = []
        self.stops = []

        self.bar_openings = []

        self.current_bar = 1

    def next(self):
            data_line = pd.Series([self.data_close[0],self.data_open[0],self.data_high[0],self.data_low[0]], index = ['Close','Open','High','Low'])
#         data_body_width = abs(self.data_close[0] - self.data_open[0])
#         upper_wick = self.data_high[0]-max(self.data_open[0],self.data_close[0])
#         lower_wick = min(self.data_close[0],self.data_open[0]) - self.data_low[0]
#         if data_body_width != 0:
#             if upper_wick/data_body_width >= self.params.min_long_wick_ratio and lower_wick/data_body_width <= self.params.max_short_wick_ratio:
# #           if ((self.data_high[0] - max(self.data_open[0],self.data_close[0]))/abs(data_body_width) >= self.params.min_long_wick_ratio
# #               and ((min(self.data_open[0],self.data_close[0]) - self.data_low[0])/abs(data_body_width)) <= self.params.max_short_wick_ratio):
            if long_criteria(data_line, self.params.min_long_wick_ratio, self.params.max_short_wick_ratio):
                # enter long bracket
                limit_price = self.data_close[0] + (self.data_high[0] - self.data_close[0])*self.params.fill_ratio
                stop_price = self.data_close[0] - (limit_price-self.data_close[0])/self.params.risk_to_reward_ratio

                bracket_buy = self.buy_bracket(limitprice=limit_price, stopprice=stop_price)
                # record the trade prices
                self.limits.append(limit_price)
                self.stops.append(stop_price)
                self.bar_openings.append(self.current_bar)
                
                
            elif short_criteria(data_line, self.params.min_long_wick_ratio, self.params.max_short_wick_ratio):
            # elif lower_wick/data_body_width >= self.params.min_long_wick_ratio and upper_wick/data_body_width <= self.params.max_short_wick_ratio:
#           elif ((self.data_high[0] - max(self.data_open[0],self.data_close[0]))/abs(data_body_width) <= self.params.max_short_wick_ratio
#               and ((min(self.data_open[0],self.data_close[0]) - self.data_low[0])/abs(data_body_width)) >= self.params.min_long_wick_ratio):
                # enter short bracket
                limit_price = self.data_close[0] - (self.data_close[0] - self.data_low[0])*self.params.fill_ratio
                stop_price = self.data_close[0] + (self.data_close[0] - limit_price)/self.params.risk_to_reward_ratio

                bracket_sell = self.sell_bracket(limitprice=limit_price, stopprice=stop_price)
                # record the trade prices
                self.limits.append(limit_price)
                self.stops.append(stop_price)
                self.bar_openings.append(self.current_bar)

            self.current_bar += 1
        
    def return_strategy_recordings(self):
        return pd.DataFrame({'Opening Bars':self.bar_openings,'Limit Prices':self.limits,'Stop Prices':self.stops})
        
        
class HangingManReversalStrategy(bt.Strategy):

    params = (
        ('min_long_wick_ratio',2.0),
        ('max_short_wick_ratio',1.0),
        ('risk_to_reward_ratio',2.0),
        ('fill_ratio',1.5)
    )

    def __init__(self):#, min_long_wick_ratio, max_short_wick_ratio, risk_to_reward_ratio):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.data_close = self.datas[0].close
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low

        self.entries = []
        self.limits = []
        self.stops = []

        self.bar_openings = []

        self.current_bar = 1

    def next(self):
        data_body_width = self.data_close[0] - self.data_open[0]
        if data_body_width != 0:
          if ((self.data_high[0] - max(self.data_open[0],self.data_close[0]))/abs(data_body_width) >= self.params.min_long_wick_ratio
              and ((min(self.data_open[0],self.data_close[0]) - self.data_low[0])/abs(data_body_width)) <= self.params.max_short_wick_ratio):
            # enter short bracket
            limit_price = self.data_close[0] - (self.data_high[0] - self.data_close[0])*self.params.fill_ratio
            stop_price = self.data_close[0] + (limit_price-self.data_close[0])/self.params.risk_to_reward_ratio

            bracket_setll = self.sell_bracket(limitprice=limit_price, stopprice=stop_price)
            # record the trade prices
            self.limits.append(limit_price)
            self.stops.append(stop_price)
            self.bar_openings.append(self.current_bar)

          elif ((self.data_high[0] - max(self.data_open[0],self.data_close[0]))/abs(data_body_width) <= self.params.max_short_wick_ratio
              and ((min(self.data_open[0],self.data_close[0]) - self.data_low[0])/abs(data_body_width)) >= self.params.min_long_wick_ratio):
            # enter long bracket
            limit_price = self.data_close[0] + (self.data_close[0] - self.data_low[0])*self.params.fill_ratio
            stop_price = self.data_close[0] - (self.data_close[0] - limit_price)/self.params.risk_to_reward_ratio

            bracket_buy = self.buy_bracket(limitprice=limit_price, stopprice=stop_price)
            # record the trade prices
            self.limits.append(limit_price)
            self.stops.append(stop_price)
            self.bar_openings.append(self.current_bar)

        self.current_bar += 1
        
    def return_strategy_recordings(self):
        return pd.DataFrame({'Opening Bars':self.bar_openings,'Limit Prices':self.limits,'Stop Prices':self.stops})
