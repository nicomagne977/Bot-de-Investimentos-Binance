"""Trading Strategy Abstract Base Class Module"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Any

class TradingStrategy(ABC):
    """
    Abstract base class for trading strategies.
    """

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add necessary indicator columns to the DataFrame and return it."""
        raise NotImplementedError

    @abstractmethod
    def check_signal(self, data: pd.DataFrame) -> str:
        """
        Inspect the (most recent) data and generated indicators and
        return one of: 'BUY', 'SELL', 'HOLD'.
        """
        raise NotImplementedError
