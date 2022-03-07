import backtrader.analyzers as btanalyzers


# -------------------------------------analyser classes - these are used for building results as the strategies run

class EnteredTrades(bt.analyzers.Analyzer):
  """
  Get the opening and closing indices for the all the trades entered and all the PNL
  """
  def create_analysis(self):
    self.opening_bars = []
    self.closing_bars = []
    self.pnls = []

  def notify_trade(self,trade):
      if trade.isclosed:
        self.pnls.append(trade.pnl)
        self.opening_bars.append(trade.baropen)
        self.closing_bars.append(trade.barclose)
        
  def get_analysis(self):
    return({'Opening Bars':self.opening_bars,
            'Closing Bars':self.closing_bars,
            'PNL':self.pnls})
  
# https://community.backtrader.com/topic/2855/how-does-the-backtrader-get-the-cash-or-value-of-each-step/2?_=1645635013496
class EquityCurve(bt.analyzers.Analyzer):
    """
    Analyzer returning cash and market values
    """
    def create_analysis(self):
        self.rets = {}
        self.vals = 0.0

    def notify_cashvalue(self, cash, value):
        self.vals = (cash, value)
        self.rets[self.strategy.datetime.datetime()] = self.vals

    def get_analysis(self):
        return {'Equity Curve':self.rets}
      
      
      
 class BracketPrices(bt.analyzers.Analyzer):
  def get_analysis(self):
    return {'Limit Prices':self.limits,
            'Stop Prices':self.stops,
            'Bar Openings':self.bar_openings}
  
  
#-------------------------evaluation functions - these use the results from the strategy-------------------------

def profit_factor_evaluation(results):
  trade_analysis = results.analyzers.trade_analysis.get_analysis()
  if 'won' not in list(trade_analysis.keys()) and 'lost' not in list(trade_analysis.keys()): # zero trades
    return 0
  elif 'won' not in list(trade_analysis.keys()): # only losing trades
    return 0
  elif 'lost' not in list(trade_analysis.keys()): # only winning trades
    return dict(trade_analysis)['won']['pnl']['total']
  else: # regular scenario - winning and losing trades
    return dict(trade_analysis)['won']['pnl']['total']/max(1,abs(dict(trade_analysis)['lost']['pnl']['total']))
  
  
def pnl_evaluation(results):
  trade_analysis = results.analyzers.trade_analysis.get_analysis()
  return dict(trade_analysis)['pnl']['gross']['total']

def get_equity_curve(results):
  equity_curve = results.analyzers.equity_curve.get_analysis()['Equity Curve']
  equity_pd = pd.DataFrame(equity_curve).T
  equity_pd.columns = ['Cash','Value']
  return equity_pd['Value']

def report_strategy_metrics(results):
  sharpe_ratio = dict(results.analyzers.mysharpe.get_analysis())['sharperatio']
  trade_analysis = results.analyzers.trade_analysis.get_analysis()
  profit_factor = profit_factor_evaluation(results)#abs(dict(trade_analysis)['won']['pnl']['total'])/max(1,abs(dict(trade_analysis)['lost']['pnl']['total']))
  equity_curve = results.analyzers.equity_curve.get_analysis()['Equity Curve']
  equity_pd = pd.DataFrame(equity_curve).T
  equity_pd.columns = ['Cash','Value']
  #equity_pd['Value'].plot()
  return_df = pd.DataFrame({'Sharpe Ratio':[sharpe_ratio],'Profit Factor':profit_factor,
                       'PNL':dict(trade_analysis)['pnl']['gross']['total'],
                       'Percent Return':dict(trade_analysis)['pnl']['gross']['total']/equity_pd.iloc[0]['Value'],
                       'Total Trades':dict(trade_analysis)['len']['total'],
                        'Long PNL':dict(trade_analysis)['long']['pnl']['total'],
                        'Short PNL':dict(trade_analysis)['short']['pnl']['total']})
  
  if 'won' not in list(trade_analysis.keys()): # only losing trades
    return_df['Win Rate'] = 0
  else: # regular scenario
    return_df['Win Rate'] = dict(trade_analysis)['won']['total']/dict(trade_analysis)['total']['total']
  return return_df

def get_rmse(results):
  equity_curve = get_equity_curve(results)
  # get only the changes in value
  changes_only = [list(summary_results)[0]]
  for i in range(1,len(summary_results)):
    if summary_results[i] != summary_results[i-1]:
      changes_only.append(summary_results[i])
  equity_fit = sm.OLS(np.array(changes_only),sm.add_constant(np.array(range(len(changes_only))))).fit()
  return math.sqrt(equity_fit.mse_resid)
