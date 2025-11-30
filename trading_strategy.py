"""
Trading strategy abstract base class module.

This module defines the abstract interface that all trading strategies must implement,
ensuring a consistent contract for signal generation and indicator calculation.
"""

from abc import ABC, abstractmethod


class TradingStrategy(ABC):
    """
    Abstract base class for trading strategies.

    This class defines the interface that all trading strategy implementations
    must follow. It establishes the contract for calculating technical indicators
    and generating trading signals (BUY, SELL, or HOLD).
    """

    @abstractmethod
    def calculate_indicators(self, data):
        """
        Calculate technical indicators based on price data.

        This abstract method must be implemented by all concrete strategy classes
        to compute the necessary technical indicators for trading decisions.

        Args:
            data: A pandas DataFrame containing OHLC (Open, High, Low, Close) price data.

        Returns:
            DataFrame: The input data with additional indicator columns.
        """
        pass

    @abstractmethod
    def check_signal(self, data) -> str:
        """
        Generate a trading signal based on price data and indicators.

        This abstract method defines the contract that all strategies must respect.
        It returns a trading signal indicating the recommended action at the current time.

        Args:
            data: A pandas DataFrame containing price data and calculated indicators.

        Returns:
            str: A trading signal - 'BUY', 'SELL', or 'HOLD'.
        """
        pass
