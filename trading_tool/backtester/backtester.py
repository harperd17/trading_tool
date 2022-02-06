import pandas as pd
import numpy as np
from tradingFunctions import *

"""class to do back testing"""

class trader:
    #def __init__(self,entries,stops,targets):
    def __init__(self,data,strategy_class,params):
        #self.strategyFunction = strategyFunction
        #self.args = args
        self.strategy_class = strategy_class
        #self.stops = [round(x,2) for x in stops]
        #self.entries = [round(x,2) for x in entries]
        #self.targets = [round(x,2) for x in targets]
        self.params = params
        self.data = data
        
    def createTrader(self):
        self.traderObject = self.strategy_class.trader_class(self.params)
        
    def findHistoricalTrades(self):
        self.entries = []
        self.stops = []
        self.targets = []
        self.directions = []
        self.successes = []
        self.trade_time = []
        self.exit_dates = []
        self.trade_dates = []
        self.profit = []
        total_profit = 0
        for i in range(self.data.shape[0]):
            if self.traderObject.check_candle(self.data.iloc[i]):
                #if the function returns true for the trade entry
                #first find the parameters from the traderObject
                self.entries.append(round(self.traderObject.entry,2))
                self.stops.append(round(self.traderObject.stop,2))
                self.targets.append(round(self.traderObject.target,2))
                self.directions.append(self.traderObject.direction)
                #now find the trade results
                self.findResult(i,self.traderObject.direction)
                
                self.successes.append(self.success)
                self.trade_time.append(self.candles_in_trade)
                self.exit_dates.append(self.data['Date'][self.exit_ind])
                self.trade_dates.append(self.data['Date'][i])
                if self.success == 1:
                    total_profit += self.traderObject.RR
                    self.profit.append(total_profit)
                else:
                    total_profit += -1
                    self.profit.append(total_profit)
            else:
                #if it isn't a trade then fill the lists with N/A's
                self.entries.append(np.nan)
                self.stops.append(np.nan)
                self.targets.append(np.nan)
                self.directions.append(np.nan)
                self.successes.append(np.nan)
                self.trade_time.append(np.nan)
                self.exit_dates.append(np.nan)
                self.trade_dates.append(self.data['Date'][i])
                self.profit.append(total_profit)
        self.backTestDataFrame = pd.DataFrame({'Entries':self.entries,'Stops':self.stops,'Targets':self.targets,
                             'Directions':self.directions,'Successes':self.successes,
                             'Trade Time':self.trade_time, 'Exit Dates':self.exit_dates,
                             'Trade Dates':self.trade_dates, 'Profit':self.profit})
        self.backTestDataFrame.set_index(pd.DatetimeIndex(self.trade_dates).tz_convert(None), drop=False, inplace=True)
        #print(self.backTestDataFrame.shape)
        #print(len(np.unique(list(self.backTestDataFrame.index))))
        # make the indices timezone naive
        #print(list(self.data.index)[0])
        #print(list(self.backTestDataFrame.index)[0])
        #print(list(self.data.index)[0] == list(self.backTestDataFrame.index)[0])
        #print(self.data.index.tzinfo)
        #print(self.backTestDataFrame.index.tzinfo)
        #print(type(self.backTestDataFrame))
        self.data.index = self.data.index.tz_localize(None)
        self.backTestDataFrame.index = self.backTestDataFrame.index.tz_localize(None)
        #print(self.data.head().index)
        #print(self.backTestDataFrame.head().index)
        self.backTestDataFrame = pd.merge(self.backTestDataFrame,self.data,how='outer',left_index=True,right_index=True)
        #print(self.backTestDataFrame.shape)
        #print(len(np.unique(list(self.backTestDataFrame.index))))
        return self.backTestDataFrame
    
    def findResult(self, i, direction):
        j = i
        if j+1 >= self.data.shape[0]-1:
            exited = True
        else:
            exited = False
        self.candles_in_trade = 0
        if direction == 1:
            #if it is a bullish trade
            while not exited:
                if self.data['Low'][j+1] <= self.traderObject.stop:
                    self.success = 0
                    self.exit_ind = j
                    exited = True
                elif self.data['High'][j+1] >= self.traderObject.target:
                    self.success = 1
                    self.exit_ind = j
                    exited = True
                else:
                    if j + 1 >= self.data.shape[0]-1:
                        #if the next i value is over the shape, then exit loop
                        exited = True
                        self.success = 0
                        self.exit_ind = j
                    else:
                        j += 1
                        self.candles_in_trade += 1
        else:
            #if it is a bearish trade
            while not exited:
                if self.data['High'][j+1] >= self.traderObject.stop:
                    self.success = 0
                    self.exit_ind = j
                    exited = True
                elif self.data['Low'][j+1] <= self.traderObject.target:
                    self.success = 1
                    self.exit_ind = j
                    exited = True
                else:
                    if j + 1 >= self.data.shape[0]-1:
                        #if the next i value is over the shape, then exit loop
                        exited = True
                        self.success = 0
                        self.exit_ind = j
                    else:
                        j += 1
                        self.candles_in_trade += 1
    def plotResults(self, data, addings, adding_types, addings_colors, sizes, within_data,legend,names):
        if len(addings) == len(adding_types) == len(addings_colors):
            apdict = []
            #if within_data is True, then the addings will be a list of column names to add to the plot
            if within_data:
                for i in range(len(addings)):
                    apdict.append(mpf.make_addplot(data[addings[i]],type= adding_types[i], color=addings_colors[i],markersize=sizes[i]))
            #if within_data is False, then the addings will be a list of dataframes to add to the plot
            else:
                for i in range(len(addings)):
                    apdict.append(mpf.make_addplot(addings[i], type=adding_types[i],color=addings_colors[i],markersize=sizes[i]))
                  
    
            if not legend:
                mpf.plot(data,type='candle',block=False,addplot=apdict,figsize = (8,10))

            else:
                mpf.plot(data,type='candle',block=False,addplot=apdict,figsize = (8,10),savefig='C:/Users/david/Desktop/Trading/Research/backtest.png')

    def plotBackTest(self, save):
        #first, I want to separate the trades into successful and unsuccessful
        win_entries = []
        lose_entries = []
        for i in range(self.backTestDataFrame.shape[0]):
            if self.backTestDataFrame['Successes'].iloc[i] == 1:
                win_entries.append(self.backTestDataFrame['Entries'].iloc[i])
                lose_entries.append(np.nan)
            elif self.backTestDataFrame['Successes'].iloc[i] == 0:
                win_entries.append(np.nan)
                lose_entries.append(self.backTestDataFrame['Entries'].iloc[i])
            else:
                win_entries.append(np.nan)
                lose_entries.append(np.nan)
        self.backTestDataFrame['Win Entries'] = win_entries
        self.backTestDataFrame['Lose Entries'] = lose_entries
            
        self.plotResults(self.backTestDataFrame,['Targets','Stops','Win Entries','Lose Entries'],['scatter']*4,['green','red','green','red'],[10]*4,True,save,False)
        
        
