import pandas as pd
import yfinance as yf

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
