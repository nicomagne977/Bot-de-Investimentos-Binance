"""
Moving Average strategy implementation module.

This module contains the concrete implementation of a moving average crossover strategy
for automated trading on the Binance exchange.
"""

from trading_strategy import TradingStrategy


class MovingAverageStrategy(TradingStrategy):
    """
    Trading strategy based on moving average crossover signals.

    This class implements a concrete trading strategy that uses two moving averages
    (short and long term) to generate buy and sell signals. The strategy generates
    a BUY signal when the short-term moving average crosses above the long-term
    moving average, and a SELL signal when it crosses below.

    Attributes:
        _short_window (int): The period for the short-term moving average (e.g., 10).
        _long_window (int): The period for the long-term moving average (e.g., 30).
    """

    def __init__(self, short_window: int, long_window: int) -> None:
        """
        Initialize the MovingAverageStrategy with window parameters.

        Args:
            short_window (int): The number of periods for the short-term moving average.
            long_window (int): The number of periods for the long-term moving average.
        """
        self._short_window = short_window
        self._long_window = long_window

    @property
    def short_window(self) -> int:
        """
        Get the short-term moving average window.

        Returns:
            int: The number of periods for the short-term moving average.
        """
        return self._short_window

    @short_window.setter
    def short_window(self, value: int) -> None:
        """
        Set the short-term moving average window.

        Args:
            value (int): The new short window period.
        """
        self._short_window = value

    @property
    def long_window(self) -> int:
        """
        Get the long-term moving average window.

        Returns:
            int: The number of periods for the long-term moving average.
        """
        return self._long_window

    @long_window.setter
    def long_window(self, value: int) -> None:
        """
        Set the long-term moving average window.

        Args:
            value (int): The new long window period.
        """
        self._long_window = value

    def calculate_indicators(self, data):
        """
        Calculate short and long-term moving averages.

        Computes the moving averages using the configured window periods
        for the provided price data. Uses pandas or numpy internally for calculations.

        Args:
            data: A pandas DataFrame containing OHLC price data.

        Returns:
            DataFrame: The input data with 'short_ma' and 'long_ma' columns added.
        """
        pass

    def check_signal(self, data) -> str:
        """
        Generate a trading signal based on moving average crossover.

        Implements the moving average crossover logic:
        - Returns 'BUY' if short MA > long MA (bullish signal)
        - Returns 'SELL' if short MA < long MA (bearish signal)
        - Returns 'HOLD' otherwise

        Args:
            data: A pandas DataFrame containing price data and moving averages.

        Returns:
            str: The trading signal - 'BUY', 'SELL', or 'HOLD'.
        """
        pass
