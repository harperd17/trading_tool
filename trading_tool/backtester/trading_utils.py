import pandas as pd
import yfinance as yf
from datetime import datetime

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

def get_normal_hour_candles(data, normal_hours_str=('9:30','16:00')):
  # this function assumes that the date is the index and is formatted
  normal_hours = [datetime.strptime(normal_hours_str[0],'%H:%M'),datetime.strptime(normal_hours_str[1],'%H:%M')]
  data['Hour'] = data.index.hour
  data['Minute'] = data.index.minute

  data['After Hour'] = data['Hour'] > normal_hours[1].hour
  data['End Hour'] = data['Hour'] == normal_hours[1].hour
  data['After Minute'] = data['Minute'] >= normal_hours[1].minute # greater than or equal because the end hour will be the start of the first after hour candle, so trading hour candles should only be less than (the opposite of greater than or equal to)

  data['Before Hour'] = data['Hour'] < normal_hours[0].hour
  data['Beginning Hour'] = data['Hour'] == normal_hours[0].hour
  data['Before Minute'] = data['Minute'] < normal_hours[0].minute

  data['After Same Hour'] = data['End Hour'] & data['After Minute']
  data['Before Same Hour'] = data['Beginning Hour'] & data['Before Minute']

  data['After Hour Candle'] = data['After Same Hour'] | data['After Hour']
  data['Before Hour Candle'] = data['Before Same Hour'] | data['Before Hour']

  data['Non Normal Hours'] = data['After Hour Candle'] | data['Before Hour Candle']

  normal_hour_pd = data[~data['Non Normal Hours']]

  normal_hour_pd = normal_hour_pd.drop(['Hour','Minute','After Hour','End Hour','After Minute','Before Hour',
                                        'Beginning Hour','Before Minute','After Same Hour','Before Same Hour',
                                        'After Hour Candle','Before Hour Candle','Non Normal Hours'], axis=1)

  return normal_hour_pd
