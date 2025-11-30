"""Moving Average Crossover Trading Strategy Module"""


import pandas as pd
from typing import Any
from trading_strategy import TradingStrategy


class MovingAverageStrategy(TradingStrategy):
    """
    Moving Average Crossover strategy implementation.

    BUY signal when short MA crosses above long MA (golden cross).
    SELL signal when short MA crosses below long MA (death cross).
    """

    def __init__(self, short_window: int = 10, long_window: int = 30) -> None:
        if short_window >= long_window:
            raise ValueError("short_window should be smaller than long_window")
        self._short_window = short_window
        self._long_window = long_window

    @property
    def short_window(self) -> int:
        return self._short_window

    @property
    def long_window(self) -> int:
        return self._long_window

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Expects `data` with a 'close' column.
        Adds:
         - 'short_ma'  : short moving average
         - 'long_ma'   : long moving average
        Returns the DataFrame with new columns.
        """
        if 'close' not in data.columns:
            raise ValueError("DataFrame must contain 'close' column")

        data = data.copy()
        data['short_ma'] = data['close'].rolling(window=self._short_window, min_periods=1).mean()
        data['long_ma'] = data['close'].rolling(window=self._long_window, min_periods=1).mean()
        return data

    def check_signal(self, data: pd.DataFrame) -> str:
        """
        Determine signal based on most recent two rows (to detect crossover).
        Returns 'BUY', 'SELL' or 'HOLD'.
        """
        if data.shape[0] < 2:
            return 'HOLD'

        df = data.dropna(subset=['short_ma', 'long_ma']).copy()
        if df.shape[0] < 2:
            return 'HOLD'

        last = df.iloc[-1]
        prev = df.iloc[-2]

        # Golden cross: prev short <= prev long and last short > last long
        if (prev['short_ma'] <= prev['long_ma']) and (last['short_ma'] > last['long_ma']):
            return 'BUY'

        # Death cross: prev short >= prev long and last short < last long
        if (prev['short_ma'] >= prev['long_ma']) and (last['short_ma'] < last['long_ma']):
            return 'SELL'

        return 'HOLD'
