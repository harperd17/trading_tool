import sys
sys.path.insert(1,'C:/Users/david/Desktop/Programming Trading/trading_tool_branches/add_jupyter_notebook/trading_tool')

from trading_tool.stock_data_collector.td_api_config import CONSUMER_KEY
import datetime
import json
import pandas as pd
from typing import Literal
import asyncio
from tda.auth import easy_client
from tda.streaming import StreamClient
import sqlite3




REDIRECT_URI = 'https://127.0.0.1'
TOKEN_PATH = 'token'
ACCOUNT_NUMBER = 490637576
API_KEY = f'{CONSUMER_KEY}@AMER.OAUTHAP'
INPUT_TZ = 'utc'
OUTPUT_TZ = 'America/New_York'

TRADING_DB_NAME = 'trading_data.db'
OPTIONS_DB_TABLE_NAME = 'options_ticks'

db_connection = sqlite3.connect(TRADING_DB_NAME)

contracts = ['AAPL_032423C152.5','AAPL_032423C155','AAPL_032423C157.5','AAPL_032423C160',
             'AAPL_032423C162.5','AAPL_032423C165']

client = easy_client(
        api_key=API_KEY,
        redirect_uri=REDIRECT_URI,
        token_path=TOKEN_PATH)

stream_client = StreamClient(client, account_id=ACCOUNT_NUMBER)



start_time = datetime.datetime.now()
quotes_df = pd.DataFrame()

latest_db_update = datetime.datetime.now()
update_cadence = datetime.timedelta(seconds=30)
collection_period = datetime.timedelta(hours=3)

def process_td_quotes_df(df: pd.DataFrame) -> pd.DataFrame:
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms').dt.tz_localize(INPUT_TZ).dt.tz_convert(OUTPUT_TZ)
    return df

def write_data_to_db(df: pd.DataFrame, db_connection, table_name: str, if_exists: Literal['fail','replace','append'] = 'append') -> None:
    df.to_sql(table_name, db_connection, if_exists=if_exists, index=False)

async def read_stream():
    #global quotes_df
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    def append_message(message):
        global quotes_df # empty dataframe to store ticks
        global process_td_quotes_df, write_data_to_db # functions
        global db_connection # database connection
        global latest_db_update # datetimes
        # create a dataframe of each quote
        quote_df = pd.DataFrame(message['content'])
        quote_df['timestamp'] = message['timestamp']
        quote_df['timestamp'] = message['timestamp']
        # convert timestamp from float to timestamp
        quotes_df = pd.concat([quotes_df, quote_df.copy()])
        if datetime.datetime.now() >= (latest_db_update + update_cadence):
            processed_quotes = process_td_quotes_df(quotes_df)
            write_data_to_db(processed_quotes, db_connection, OPTIONS_DB_TABLE_NAME)
            quotes_df = pd.DataFrame()
            latest_db_update = datetime.datetime.now()
        

    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_level_one_option_handler(append_message)
    await stream_client.level_one_option_subs(contracts)

    while datetime.datetime.now() < start_time + collection_period:
        await stream_client.handle_message()

async def close_stream():
    await stream_client.level_one_option_unsubs(contracts)

asyncio.run(read_stream())
breakpoint()
asyncio.run(close_stream())

breakpoint()

