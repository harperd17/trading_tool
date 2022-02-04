from distutils.core import setup

setup(name='trading_tool',
      version='0.1',
      description='Library for Collecting data and building trading strategies',
      author='David Harper',
      author_email='spice.algo.man@gmail.com',
      packages=['stock_data_collector','backtester','trading_strategies'],
     )
