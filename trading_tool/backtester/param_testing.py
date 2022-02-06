# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 17:20:36 2021

@author: david
"""
import pandas as pd
#import data_utils
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
from tradingFunctions import *
from trading_tool.strategies import HangingManClass
from trading_tool import backTester
import itertools

class testParams():
    def __init__(self,strategy_class, params_to_test):
        self.strategy = strategy_class
        self.params_to_test = params_to_test

    def test_values(self, data):
        # the params brought in thorugh params_to_test will either be
        # a tuple or a single value
        # create a list of the cartesian product of all the sets of values to test
        keys = []
        items = []
        for key in self.params_to_test:
            keys.append(key)
            if not isinstance(self.params_to_test[key],tuple) and not isinstance(self.params_to_test[key],list):
                items.append([self.params_to_test[key]])
            else:
                items.append(self.params_to_test[key])
        testing_combos = list(itertools.product(*items))
        for param in testing_combos:
            param_line = {}
            for i in range(len(keys)):
                param_line[keys[i]] = param[i]
            print(param_line)
            back_test_object = backTester.trader(data,self.strategy,param_line)
            back_test_object.createTrader()
            backTestData = back_test_object.findHistoricalTrades()
            successes = backTestData['Successes']
            occurences = []
            for s in successes:
                if np.isnan(s):
                    occurences.append(0)
                else:
                    occurences.append(1)
            var_name = ''
            for p in param_line:
                var_name += str(p) + "-"
            data[var_name+'Occurrences'] = occurences
            data[var_name+'Successes'] = successes
        return data
