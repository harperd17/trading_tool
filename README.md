# trading_tool

## Introduction
This tool is used for building trading strategies. Unlike normal backtesting platforms, this is able to take in a set of input parameters and test different combinations of them. Then, you can find the optimal combination of strategy parameters.

## Parts of the Tool
#### backTester
#### Steps:
This class is used for performing a backtest of a given strategy with a single set of parameters for the strategy.
1. Instatiate the "trader" class, passing in the data, trading strategy module, and parameters as input.
2. Call the "createTrader" method.
3. Call the "findHistoricalTrades" method to loop through the data and find all instances that match the specifications for a trade entry and determine which were successful and which weren't. Access the back test results using the "backTestDataFrame" attribute.
4. The results can be plotted by calling the "plotBackTest" method and passing in the file location for saving the plot.

#### param_testing
This contains a class called "testParams" which allows you to test a whole variety of parameters for trading strategy module. Again, the trading strategy needs to have a "trader" class inside it.
#### Steps:
1. Instatiate the "testParams" class by passing in the trading strategy module and the didctionary containing the name of the strategy parameters as keys and the values to be tested as their values. 
2. Call the method "test_values", passing in the data set to use for the backtests. This returns a pandas data frame with the occurences and successes marked in their own columns

