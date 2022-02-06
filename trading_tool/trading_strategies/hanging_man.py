# -*- coding: utf-8 -*-
"""
Created on Sat May 22 14:44:04 2021

@author: david
"""


class trader_class():
    def __init__(self,params):
        #params is a dictionary with all the required parameters
        self.H1 = params['H1']
        self.H2 = params['H2']
        self.S1 = params['S1']
        self.S2 = params['S2']
        self.RR = params['S1']
        self.param_names = ('H1','H2','S1','S2','Param Split')
        try:
            self.lower_thresh = params['Lower Thresh']
            self.upper_thresh = params['Upper Thresh']
        except:
            pass
        self.param_split = params['Param Split']
        if self.param_split:
            self.H1_2 = params['H1_2']
            self.H2_2 = params['H2_2']
            self.param_names = ('H1','H1_2','H2','H2_2','S1','S2','Param Split')
        else:
            self.H1_2 = ""
            self.H2_2 = ""
        
    def findHangingMans(self, data, w_b_ratio1, w_b_ratio2, split, r1_2, r2_2):
        """
        This function finds occurences of the hanging man candlestick pattern
        Parameters:
        data: dataframe
            Is the dataframe that is being searched for hanging man occurrences
        w_b_ratio1: float
            Is the minimum ratio of the tall top/bottom wick length to body length. This is the top wick for green candles and bottom wick for red candles.
        w_b_ratio2: float
            Is the maximum ratio of the short top/bottom wik length to body length. This is the bottom wick for green candles and top wick for red candles.
            
        Returns:
            list of indeces for hanging man occurences - 1 for occurrence, 0 for non occurence
        """
        
        body_lengths = data['Close']-data['Open']
        occurrences = []
        #for i in range(data.shape[0]):
        top_wick = data['High'] - max(data['Close'],data['Open'])
        bottom_wick = min(data['Close'],data['Open']) - data['Low']
        #check to see if it is cutoff by high and low
        if split:
            #check to see if candle is neutral
            if body_lengths == 0:
                #if it's a neutral candle, then treat either the top or bottom wick as the body to compare to the other wick
                if (top_wick >= w_b_ratio1*bottom_wick and top_wick < r1_2*bottom_wick) or (bottom_wick >= w_b_ratio1*top_wick and bottom_wick < r1_2*top_wick):
                    occurrences.append(1)
                else:
                    occurrences.append(0)
            else:
                if ((bottom_wick >= w_b_ratio1*abs(body_lengths) and bottom_wick < r1_2*abs(body_lengths)) and (top_wick <= w_b_ratio2*abs(body_lengths) and top_wick > r2_2*abs(body_lengths)) and body_lengths < 0) or ((top_wick >= w_b_ratio1*abs(body_lengths) and top_wick < r1_2*abs(body_lengths)) and (bottom_wick <= w_b_ratio2*abs(body_lengths) and bottom_wick > r2_2*abs(body_lengths)) and body_lengths>0):
                    occurrences.append(1)
                else:
                    occurrences.append(0)   
        else:
            #check to see if candle is neutral
            if body_lengths == 0:
                #if it's a neutral candle, then treat either the top or bottom wick as the body to compare to the other wick
                if top_wick >= w_b_ratio1*bottom_wick or bottom_wick >= w_b_ratio1*top_wick:
                    occurrences.append(1)
                else:
                    occurrences.append(0)
            else:
                if (bottom_wick >= w_b_ratio1*abs(body_lengths) and top_wick <= w_b_ratio2*abs(body_lengths) and body_lengths < 0) or (top_wick >= w_b_ratio1*abs(body_lengths) and bottom_wick <= w_b_ratio2*abs(body_lengths) and body_lengths > 0):
                    occurrences.append(1)
                else:
                    occurrences.append(0)   
        if occurrences[0] == 1:
            return True
        else:
            return False

    
    def hangingManParams(self, data, s1, s2):
        """
        This function takes in a candle and the s1 and s2 parameters and returns
        the take profit and stop loss for the trade:
        data: dataframe
            Is the dataframe with the one candle of data
        s1: float
            Ratio of reward to risk.
        s2: float
            Ratio of the tall wick that we are looking to get filled.
            
        Returns:
            dictionary containing the trade entry parameters
        """
        
        entry_side = ''
        exit_side = ''
        #first find out if it is bullish or bearish move
        #if bullish
        if (data['High'] - max(data['Close'],data['Open'])) >= (min(data['Close'],data['Open']) - data['Low']):
            target = data['Close'] + (data['High'] - data['Close'])*s2
            stop = data['Close'] - (target - data['Close'])/s1
            entry_side = "buy"
            exit_side = 'sell'
        #bearish
        else:
            target = data['Close'] - (data['Close'] - data['Low'])*s2
            stop = data['Close'] + (data['Close']-target)/s1
            entry_side = "sell"
            exit_side = 'buy'
        order_details = {'entry_side':entry_side,'exit_side':exit_side,'take_profit':target,'stop_price':stop}       
        return order_details
        
    def check_candle(self,data):
        try:
            data = data.copy().loc[(self.lower_thresh <= data['High']-data['Low']) <= self.upper_thresh]
        except:
            pass
        if data.shape[0] == 0:
            return False
        else:
            if self.findHangingMans(data, self.H1, self.H2, self.param_split, self.H1_2, self.H2_2):
                #if the candle is tradable then find entry, stop, and target
                self.entry = round(data['Close'],2)
                
                self.order_params = self.hangingManParams(data, self.S1, self.S2)
                if self.order_params['entry_side'] == 'buy':
                    self.direction = 1
                else:
                    self.direction = -1
                self.target = round(self.order_params['take_profit'],2)
                self.stop = round(self.order_params['stop_price'],2)
                return True
            else:
                return False
