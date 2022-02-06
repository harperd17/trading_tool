import pandas as pd
from datetime import datetime, timedelta
import os
import yfinance as yf
import argparse
import trading_tool
from trading_tool.backtester import get_prior_data, get_stock_symbols, format_index, get_stock_data

# set up the folder path
FOLDER_PATH = '/content/drive/MyDrive/Trading/Data'
# set up the time frames of interest and the stock symbols
TIME_FRAMES = ('2m','5m','15m','30m','90m')
SYMBOLS = get_stock_symbols()
# now start to gather the data - first, I need todays date so the program knows what date to back to in gathering the data
TODAY_DATE = datetime.today()

# go through all the symbols and time frames and append new data to the existing data (if applicable)
for symbol in SYMBOLS:
  for time_frame in TIME_FRAMES:
    print("Symbol: {}, Time Frame: {}".format(symbol,time_frame))
    # get the new data - there are different lookback periods allowed depending on the data granularity so I must check the time frame first
    if time_frame == '1m':
      new_data = get_stock_data(symbol, TODAY_DATE - timedelta(days=4),TODAY_DATE,time_frame)
    else:
      new_data = get_stock_data(symbol, TODAY_DATE - timedelta(days=59),TODAY_DATE,time_frame)
    # determine if a file already exists for this symbol and time frame - if so then append the new data and save
    if os.path.isfile(FOLDER_PATH+'/'+symbol+time_frame+'Data.csv'): 
      # get the existing data
      prior_data = get_prior_data(FOLDER_PATH+'/'+symbol+time_frame+'Data.csv')
      # concatenate the new dataframe onto the old dataframe and remove any duplicates, using the index as a judge for duplicates
      all_data = pd.concat((prior_data,new_data))
      all_data = all_data[~all_data.index.duplicated(keep='first')]
      # now save the concatenated data to overwrite the file
      all_data.to_csv(FOLDER_PATH+'/'+symbol+time_frame+'Data.csv')
    else:
      new_data.to_csv(FOLDER_PATH+'/'+symbol+time_frame+'Data.csv')
