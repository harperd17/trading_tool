import backtrader as bt
import statsmodels.api as sm
import pandas as pd
import numpy as np
from copy import deepcopy


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

def get_trade_analysis(results):
    trade_analysis_format = {
      'won':{'pnl':{'total':0},'total':0},
      'lost':{'pnl':{'total':0},'total':0},
      'pnl':{'gross':{'total':0}},
      'len':{'total':0},
      'long':{'pnl':{'total':0}},
      'short':{'pnl':{'total':0}},
    }
    final_trade_analysis = trade_analysis_format.copy()    
    trade_analysis = dict(results.analyzers.trade_analysis.get_analysis())
    final_trade_analysis.update(trade_analysis)
    return final_trade_analysis

def get_entered_trades(results):
    entered_trades = results.analyzers.entered_trades.get_analysis()
    return pd.DataFrame(entered_trades)
  
  
def profit_factor_evaluation(results):
  # trade_analysis = results.analyzers.trade_analysis.get_analysis()
  trade_analysis = get_trade_analysis(results)
  # if 'won' not in list(trade_analysis.keys()) and 'lost' not in list(trade_analysis.keys()): # zero trades
  #   return 0
  # elif 'won' not in list(trade_analysis.keys()): # only losing trades
  #   return 0
  # elif 'lost' not in list(trade_analysis.keys()): # only winning trades
  #   return dict(trade_analysis)['won']['pnl']['total']
  # else: # regular scenario - winning and losing trades
  return trade_analysis['won']['pnl']['total']/max(1,abs(trade_analysis['lost']['pnl']['total']))
  
  
def pnl_evaluation(results):
  # trade_analysis = results.analyzers.trade_analysis.get_analysis()
  trade_analysis = get_trade_analysis(results)
  return trade_analysis['pnl']['gross']['total']

def get_equity_curve(results):
  equity_curve = results.analyzers.equity_curve.get_analysis()['Equity Curve']
  equity_pd = pd.DataFrame(equity_curve).T
  equity_pd.columns = ['Cash','Value']
  return equity_pd['Value']

def report_strategy_metrics(results):
  sharpe_ratio = dict(results.analyzers.mysharpe.get_analysis())['sharperatio']
#   trade_analysis = results.analyzers.trade_analysis.get_analysis()
  trade_analysis = get_trade_analysis(results)
  profit_factor = profit_factor_evaluation(results)#abs(dict(trade_analysis)['won']['pnl']['total'])/max(1,abs(dict(trade_analysis)['lost']['pnl']['total']))
  equity_curve = results.analyzers.equity_curve.get_analysis()['Equity Curve']
  equity_pd = pd.DataFrame(equity_curve).T
  equity_pd.columns = ['Cash','Value']
  #equity_pd['Value'].plot()
  return_df = pd.DataFrame({'Sharpe Ratio':[sharpe_ratio],'Profit Factor':profit_factor,
                       'PNL':dict(trade_analysis)['pnl']['gross']['total'],
                       'Percent Return':dict(trade_analysis)['pnl']['gross']['total']/equity_pd.iloc[0]['Value'],
                       'Total Trades':trade_analysis['long']['total'] + trade_analysis['short']['total'],
                        'Long PNL':dict(trade_analysis)['long']['pnl']['total'],
                        'Short PNL':dict(trade_analysis)['short']['pnl']['total']})
  
#   if 'won' not in list(trade_analysis.keys()): # only losing trades
#     return_df['Win Rate'] = 0
#   else: # regular scenario
  return_df['Win Rate'] = trade_analysis['won']['total']/(trade_analysis['won']['total']+trade_analysis['lost']['total'])
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

def get_equity_curve_model(results):
  equity_curve = get_equity_curve(results)
  # get only the changes in value
  changes_only = [list(equity_curve)[0]]
  for i in range(1,len(equity_curve)):
    if equity_curve[i] != equity_curve[i-1]:
      changes_only.append(equity_curve[i])
  equity_fit = sm.OLS(np.array(changes_only),sm.add_constant(np.array(range(len(changes_only))))).fit()
  return equity_fit


def run_strategy(data, StrategyClass, analyzers, evaluation_func, strategy_params_dict = None, DataClass=bt.feeds.PandasData, cash_level=1000000.0, size = 100):
  if not isinstance(data,list):
    data=[data]
  for dat in data:
    # set up the cerebro
    cerebro = bt.Cerebro()
    #cerebro.adddata(DataClass(dataname = dat))
    cerebro.adddata(bt.feeds.PandasData(dataname = dat))
    cerebro.broker.setcash(cash_level)  
    cerebro.addsizer(bt.sizers.SizerFix, stake=size)
    if strategy_params_dict is None:
      cerebro.addstrategy(StrategyClass)
    else:
      cerebro.addstrategy(StrategyClass, **strategy_params_dict)
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    for analyzer_name in analyzers:
      cerebro.addanalyzer(deepcopy(analyzers[analyzer_name], _name=analyzer_name))
    run_result = cerebro.run()[0]
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    strategy_evaluation = evaluation_func(run_result)
    return strategy_evaluation
