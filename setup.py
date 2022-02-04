from distutils.core import setup

setup(name='trading_tool',
      version='0.1',
      description='Library for Collecting data and building trading strategies',
      url = 'https://github.com/harperd17/trading_tool',
      author='David Harper',
      author_email='spice.algo.man@gmail.com',
      py_modules=['stock_data_collector','backtester','trading_strategies'],#packages
     )
