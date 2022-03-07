import optuna
import pandas as pd
import matplotlib.pyplot as plt
from trading_tool.backtester.strategy_evaluation import report_strategy_metrics, run_strategy

# silence all the print outs from optuna
# https://github.com/optuna/optuna/issues/1789
# https://optuna.readthedocs.io/en/latest/faq.html#how-to-suppress-log-messages-of-optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

class ParameterOptimizer():
  def __init__(self):
    ...

  def get_optimized_parameters(self, training_sets, validation_sets, StrategyClass, evaluation_func, optimization_func, params, sizing_func, analyzers, initial_cash = 1000000, unique_validation_sets=True, direction='minimize', n_trials=50, strategy_report = report_strategy_metrics):
    self.optimal_params_list = []
    self.params = params
    if unique_validation_sets:
      self.equity_curves = []
    else:
      self.equity_curves = [[]]
    self.strategy_metrics_list = []
    cash_level = initial_cash
    for train_fold, validation_fold in list(zip(training_sets, validation_sets)):
      def fold_objective(trial):
        dict_of_suggested_params = {}
        for p in self.params:
          dict_of_suggested_params[p] = trial.suggest_float(p,self.params[p][0],self.params[p][1])
        train_results = run_strategy(train_fold.copy(), StrategyClass, analyzers, evaluation_func, size = sizing_func(initial_cash, train_fold), strategy_params_dict=dict_of_suggested_params)
        validation_results = run_strategy(validation_fold.copy(), StrategyClass, analyzers, evaluation_func, size = sizing_func(initial_cash, train_fold), strategy_params_dict=dict_of_suggested_params)

        return optimization_func(train_results, validation_results)


      study = optuna.create_study(direction=direction)
      study.optimize(fold_objective, n_trials=n_trials) 
      self.optimal_params_list.append(study.best_params)

      fold_metrics = run_strategy(validation_fold.copy(), StrategyClass, analyzers, report_strategy_metrics, cash_level =cash_level, size = sizing_func(cash_level, validation_fold), strategy_params_dict=study.best_params)
      self.strategy_metrics_list.append(fold_metrics)
      validation_equity_curve = run_strategy(validation_fold.copy(), StrategyClass, analyzers, get_equity_curve, cash_level = cash_level, size = sizing_func(cash_level, validation_fold), strategy_params_dict=study.best_params)
      if unique_validation_sets:
        self.equity_curves.append(validation_equity_curve)
      else:
        self.equity_curves[0] += list(validation_equity_curve)
      cash_level = validation_equity_curve[-1]

  def get_optimal_params_df(self):
    # https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    return pd.DataFrame({k: [dic[k] for dic in self.optimal_params_list] for k in self.optimal_params_list[0]})

  def get_strategy_summary_df(self):
    strat_summary = pd.concat((self.strategy_metrics_list))
    strat_summary['Return Per Trade'] = strat_summary['Percent Return']/strat_summary['Total Trades']
    return strat_summary

  def plot_optimal_params(self):
    min_param = 0
    max_param = 0
    for p in self.params:
      if self.params[p][0] < min_param:
        min_param = self.params[p][0]
      if self.params[p][1] > max_param:
        max_param = self.params[p][1]
    optimal_params_df = self.get_optimal_params_df()
    for col in optimal_params_df.columns:
      optimal_params_df[col].plot(label=col)
    plt.ylim(min_param, max_param+5)
    plt.legend()

  def plot_validation_equity_curves(self):
    for eq in self.equity_curves:
      plt.plot(eq)



# # -*- coding: utf-8 -*-
# """
# Created on Wed Aug 18 17:20:36 2021

# @author: david
# """
# import pandas as pd
# #import data_utils
# from datetime import datetime
# import numpy as np
# import matplotlib.pyplot as plt
# import os
# from tradingFunctions import *
# from trading_tool.strategies import HangingManClass
# from trading_tool import backTester
# import itertools

# class testParams():
#     def __init__(self,strategy_class, params_to_test):
#         self.strategy = strategy_class
#         self.params_to_test = params_to_test

#     def test_values(self, data):
#         # the params brought in thorugh params_to_test will either be
#         # a tuple or a single value
#         # create a list of the cartesian product of all the sets of values to test
#         keys = []
#         items = []
#         for key in self.params_to_test:
#             keys.append(key)
#             if not isinstance(self.params_to_test[key],tuple) and not isinstance(self.params_to_test[key],list):
#                 items.append([self.params_to_test[key]])
#             else:
#                 items.append(self.params_to_test[key])
#         testing_combos = list(itertools.product(*items))
#         for param in testing_combos:
#             param_line = {}
#             for i in range(len(keys)):
#                 param_line[keys[i]] = param[i]
#             print(param_line)
#             back_test_object = backTester.trader(data,self.strategy,param_line)
#             back_test_object.createTrader()
#             backTestData = back_test_object.findHistoricalTrades()
#             successes = backTestData['Successes']
#             occurences = []
#             for s in successes:
#                 if np.isnan(s):
#                     occurences.append(0)
#                 else:
#                     occurences.append(1)
#             var_name = ''
#             for p in param_line:
#                 var_name += str(p) + "-"
#             data[var_name+'Occurrences'] = occurences
#             data[var_name+'Successes'] = successes
#         return data
