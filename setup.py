from distutils.core import setup

setup(name='trading_tool',
      version='0.1',
      description='Library for Collecting data and building trading strategies',
      url = 'https://github.com/harperd17/trading_tool',
      author='David Harper',
      author_email='spice.algo.man@gmail.com',
      #package_dir = {'': 'trading_tool'},
      packages=['trading_tool','trading_tool.stock_data_collector','trading_tool.backtester','trading_tool.trading_strategies'],
     )
