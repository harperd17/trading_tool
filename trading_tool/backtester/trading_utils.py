import pandas as pd
import yfinance as yf
from datetime import datetime
import pandas_market_calendars as mcal
import numpy as np


def get_prior_data(file_path: str, fields: tuple = ('High','Low','Open','Close','Volume'),index_col: str = 'Date'):
  data = pd.read_csv(file_path,index_col=index_col)[list(fields)]
  data = format_index(data)
  return data

def get_stock_symbols(file_path: str = None):
  if not file_path:
    return ('BAC','UBER','GE','MU','T','MSFT',
            'AAPL','SPY','SNAP','F','GOOGL','FB',
            'AMZN','NFLX','BA','INTC','CSCO','AMD',
            'DIS','NVDA')
  else:
    symbols = pd.read_csv(file_path)
    return tuple(symbols["Symbols"])
  
def format_index(data: pd.DataFrame, date_format: str = '%Y-%m-%d %H:%M:%S'):
  # formatting the dates to have a consistent format and UTC to hopefully avoid problems if date format later changes like it has before from yfinance
  data = data.set_index(pd.DatetimeIndex(pd.to_datetime(data.index,format=date_format,utc=True)))
  data.index.name = 'Date'
  return data

def get_stock_data(symbol: str, start_date: str, end_date:str, interval: str = '1d',prepost: bool = False ,period = None, fields: tuple = ('High','Low','Open','Close','Volume')):
  # if period isn't 'None' then the user passed in something, usually 'max'
  if not period is None:
      stock_data = yf.download(symbol,period=period,prepost=prepost,interval=interval,actions=False)[list(fields)]
  else:
      stock_data = yf.download(symbol,start=start_date,end=end_date,interval=interval,prepost=prepost,actions=False)[list(fields)]
  # the stock data comes in with no 'Date' column, but rather the 'Date' is the index, which needs to be formatted to ensure consistency over time
  stock_data = format_index(stock_data)
  return stock_data

def correct_high_low_outliers(data, std_thresh=3.0):
  data['Top Wicks'] = data['High'] - data[['Open','Close']].max(axis=1)
  data['Bottom Wicks'] = data[['Open','Close']].min(axis=1) - data['Low']
  all_wicks = pd.concat((data['Top Wicks'], data['Bottom Wicks']))

  wick_means = all_wicks.mean()
  wick_std = all_wicks.std()

  std_thresh = 3.0
  data['Wick Thresh'] = wick_means + wick_std * std_thresh

  data['Non Outlier Lower Wick'] = data['Bottom Wicks'] < data['Wick Thresh']
  data['Non Outlier Upper Wick'] = data['Top Wicks'] < data['Wick Thresh']

  data['New Top Wicks'] = data['Non Outlier Upper Wick'] * data['High'] + (~data['Non Outlier Upper Wick']) * data[['Open','Close']].max(axis=1)
  data['New Bottom Wicks'] = data['Non Outlier Lower Wick'] * data['Low'] + (~data['Non Outlier Lower Wick']) * data[['Open','Close']].min(axis=1)

  data['High'] = data['New Top Wicks']
  data['Low'] = data['New Bottom Wicks']

  data = data.drop(['Top Wicks','Bottom Wicks','Wick Thresh','Non Outlier Lower Wick','Non Outlier Upper Wick','New Top Wicks','New Bottom Wicks'], axis=1)

  return data

# this function below isn't used anymore and a better one, named "get_trading_hour_candles" is used

# def get_normal_hour_candles(data, normal_hours_str=('9:30','16:00')):
#   # this function assumes that the date is the index and is formatted
#   normal_hours = [datetime.strptime(normal_hours_str[0],'%H:%M'),datetime.strptime(normal_hours_str[1],'%H:%M')]
#   data['Hour'] = data.index.hour
#   data['Minute'] = data.index.minute

#   data['After Hour'] = data['Hour'] > normal_hours[1].hour
#   data['End Hour'] = data['Hour'] == normal_hours[1].hour
#   data['After Minute'] = data['Minute'] >= normal_hours[1].minute # greater than or equal because the end hour will be the start of the first after hour candle, so trading hour candles should only be less than (the opposite of greater than or equal to)

#   data['Before Hour'] = data['Hour'] < normal_hours[0].hour
#   data['Beginning Hour'] = data['Hour'] == normal_hours[0].hour
#   data['Before Minute'] = data['Minute'] < normal_hours[0].minute

#   data['After Same Hour'] = data['End Hour'] & data['After Minute']
#   data['Before Same Hour'] = data['Beginning Hour'] & data['Before Minute']

#   data['After Hour Candle'] = data['After Same Hour'] | data['After Hour']
#   data['Before Hour Candle'] = data['Before Same Hour'] | data['Before Hour']

#   data['Non Normal Hours'] = data['After Hour Candle'] | data['Before Hour Candle']

#   normal_hour_pd = data[~data['Non Normal Hours']]

#   normal_hour_pd = normal_hour_pd.drop(['Hour','Minute','After Hour','End Hour','After Minute','Before Hour',
#                                         'Beginning Hour','Before Minute','After Same Hour','Before Same Hour',
#                                         'After Hour Candle','Before Hour Candle','Non Normal Hours'], axis=1)

#   return normal_hour_pd


def correct_calendar(incorrect_calendar):
  # first, I find where the start hour is 13
  incorrect_calendar['correct open'] = incorrect_calendar['market_open'].dt.hour == 13

  # now I make a new dataframe that has an offset of 4 hours for the applicable rows
  four_hour_offset_open = incorrect_calendar[incorrect_calendar['correct open']]['market_open'] - pd.DateOffset(hours=4)
  four_hour_offset_close = incorrect_calendar[incorrect_calendar['correct open']]['market_close'] - pd.DateOffset(hours=4)
  four_hour_offset = pd.merge(four_hour_offset_open,four_hour_offset_close,left_index=True,right_index=True)

  # now I make a new dataframe that an offset of 5 hours for the remaining rows
  five_hour_offset_open = incorrect_calendar[~incorrect_calendar['correct open']]['market_open'] - pd.DateOffset(hours=5)
  five_hour_offset_close = incorrect_calendar[~incorrect_calendar['correct open']]['market_close'] - pd.DateOffset(hours=5)
  five_hour_offset = pd.merge(five_hour_offset_open,five_hour_offset_close,left_index=True,right_index=True)

  # concatenate the four hour and five hour offset dataframes - these are likely in the correct order of dates, but if they aren't this shouldn't matter
  # since this calendar will be joined with the stock data later on, so the order won't matter
  corrected_calendar = pd.concat((four_hour_offset, five_hour_offset))

  return corrected_calendar

def get_trading_hour_candles(data, trading_calendar):
  # get only the date part of the datetime - just has the hours, minutes, etc. extracted
  data['Date Part'] = pd.to_datetime(data.index.date)
  # merge the data with the trading calendar based on the date part
  data_merged = pd.merge(data, trading_calendar, left_on='Date Part', right_index=True)
  # make a new column that determines whether or not each row of data is within the trading hours of that day
  data_merged['Within Hours'] = (data_merged.index > data_merged['market_open']) & (data_merged.index < data_merged['market_close'])
  trading_hours_data = data_merged[data_merged['Within Hours']]
  trading_hours_data = trading_hours_data.drop(['Date Part','market_open','market_close','Within Hours'],axis=1)
  return trading_hours_data



def break_data_into_chunks(data, trading_calendar):
  data_shape = data.copy().shape
  # get the unique dates
  unique_data_dates = pd.to_datetime(data.index.date).unique()
  unique_calendar_dates = trading_calendar.index.unique()
  all_dates = pd.merge(
      pd.DataFrame(unique_data_dates, index=unique_data_dates,columns=['Data Dates']),
      pd.DataFrame(unique_calendar_dates, index=unique_calendar_dates, columns=['Calendar Dates']),
      left_index=True, right_index=True,how='outer')
  
  # now I can find where there are gaps in the dates within the data. Now, I just need to find out how many unique chunks of gaps there are -
  # i.e. are they all next to each other? (signigying only one grouping), or are they broken up by other data dates? (signifying more than one chunk of missing data)
  # first, create a column that is simply 0,1,2,...
  all_dates['Order'] = range(all_dates.shape[0])

  # now remove the nulls in 'Data Dates'
  all_dates = all_dates[~all_dates['Data Dates'].isnull()]

  # now, I create a 'Last Order' column which is simply the 'Order' from the previous row - I drop na afterward
  last_order = [np.nan]
  last_order += list(all_dates['Order'])[:-1]
  all_dates['Last Order'] = last_order
  all_dates = all_dates.dropna()

  # now make a row which determines whether or not the 'Order' is 'Last Order' + 1. If it isn't, there was a gap in the data dates which was removed from ~.isnull()
  # since all the missing dates in the data were removed from this dataframe, each unique chunk of missing data will only pop up once, and each unique missing chunk will
  all_dates['Correct Order'] = all_dates['Order'] == all_dates['Last Order'] + 1

  # since the rows where the 'Correct Order' is False signify the start of a new chunk, I need to break up the data into chunks based off this
  chunk_beginning_dates = all_dates[~all_dates['Correct Order']]['Data Dates']

  # I have to create the 'Date Part' column to get a timezone unawaire representation of the date
  data['Date Part'] = data.index.date

  data_chunks = []
  for date in chunk_beginning_dates:
    # append a dataframe that contains all candles with a date less than the current date being evaluated
    data_chunks.append(data[data['Date Part']<date].copy())
    # now remove the section of the dataframe that was just extracted and appended to the 'data_chunks' list
    data = data[data['Date Part']>=date]
  # now that I've gone through all the dates that signify gaps, I will append what is left of the data - first, I'll make sure it isn't empty
  if data.shape[0] > 0:
    data_chunks.append(data.copy())

  # now to perform a quick check to make sure the lengths all add up properly
  running_total_length = 0
  for chunk in data_chunks:
    running_total_length += chunk.shape[0]
  if running_total_length != data_shape[0]:
    raise ValueError('The sum of the chunks lengths is {} but the original data has length {}. David, you must figure out what happened and revise the "break_data_into_chunks" function accordingly.'.format(running_total_length,data_shape[0]))
  return data_chunks


def get_exchange_calendar(data = None, exchange_name='NYSE', calendar_start_date = None, calendar_end_date = None):
  exchange_calendar = mcal.get_calendar(exchange_name)
  # if data is provided then infer the start and end dates from the data
  if not data is None:
    calendar_start_date = data.index.min()
    calendar_end_date = data.index.max()
  return correct_calendar(exchange_calendar.schedule(start_date = calendar_start_date,end_date = calendar_end_date))
