from setuptools import find_packages, setup

setup(name='trading_tool',
      version='0.1',
      description='Library for Collecting data, building trading strategies, and backtesting them.',
      url = 'https://github.com/harperd17/trading_tool',
      author='David Harper',
      author_email='spice.algo.man@gmail.com',
      package_dir = {"": "trading_tool"},
      packages = find_packages(where="trading_tool")
      #packages=['trading_tool','trading_tool.stock_data_collector','trading_tool.backtester','trading_tool.trading_strategies'],
     )
