"""
Main application module for the Binance trading bot.

This module contains the primary orchestrator class that manages all components
of the trading bot including configuration, execution, and real-time status display.
"""

from typing import Optional, Dict, Any
from binance_client import BinanceClient
from portfolio import Portfolio
from trading_strategy import TradingStrategy
from data_manager import DataManager


class App:
    """
    Main application class that orchestrates all trading bot components.

    This class is the central coordinator responsible for managing all other
    components (BinanceClient, Portfolio, TradingStrategy, DataManager). It handles
    user configuration, contains the main trading loop, and provides real-time
    status information. The class interacts with users through console or GUI
    and executes trading orders based on strategy signals.

    Attributes:
        _is_running (bool): Flag indicating if the bot is currently active.
        _pair (str): The trading pair symbol (e.g., 'BTCUSDT').
        _capital (float): The initial capital allocated for trading in USDT.
        _binance_client (BinanceClient): Client for Binance API communication.
        _portfolio (Portfolio): Portfolio manager for tracking balances and trades.
        _strategy (TradingStrategy): The trading strategy implementation.
        _data_manager (DataManager): Manager for data persistence.
    """

    def __init__(self) -> None:
        """Initialize the App with default values."""
        self._is_running = False
        self._pair: Optional[str] = None
        self._capital = 0.0
        self._binance_client: Optional[BinanceClient] = None
        self._portfolio: Optional[Portfolio] = None
        self._strategy: Optional[TradingStrategy] = None
        self._data_manager = DataManager()

    @property
    def is_running(self) -> bool:
        """
        Get the running status of the bot.

        Returns:
            bool: True if the bot is running, False otherwise.
        """
        return self._is_running

    @is_running.setter
    def is_running(self, value: bool) -> None:
        """
        Set the running status of the bot.

        Args:
            value (bool): True to mark the bot as running, False to stop it.
        """
        self._is_running = value

    @property
    def pair(self) -> Optional[str]:
        """
        Get the trading pair.

        Returns:
            str: The trading pair symbol (e.g., 'BTCUSDT').
        """
        return self._pair

    @pair.setter
    def pair(self, value: str) -> None:
        """
        Set the trading pair.

        Args:
            value (str): The trading pair symbol.
        """
        self._pair = value

    @property
    def capital(self) -> float:
        """
        Get the trading capital amount.

        Returns:
            float: The capital allocated for trading in USDT.
        """
        return self._capital

    @capital.setter
    def capital(self, value: float) -> None:
        """
        Set the trading capital amount.

        Args:
            value (float): The capital amount in USDT.
        """
        self._capital = value

    @property
    def binance_client(self) -> Optional[BinanceClient]:
        """
        Get the Binance API client.

        Returns:
            BinanceClient: The Binance client instance.
        """
        return self._binance_client

    @binance_client.setter
    def binance_client(self, value: BinanceClient) -> None:
        """
        Set the Binance API client.

        Args:
            value (BinanceClient): The Binance client instance.
        """
        self._binance_client = value

    @property
    def portfolio(self) -> Optional[Portfolio]:
        """
        Get the portfolio manager.

        Returns:
            Portfolio: The portfolio manager instance.
        """
        return self._portfolio

    @portfolio.setter
    def portfolio(self, value: Portfolio) -> None:
        """
        Set the portfolio manager.

        Args:
            value (Portfolio): The portfolio manager instance.
        """
        self._portfolio = value

    @property
    def strategy(self) -> Optional[TradingStrategy]:
        """
        Get the trading strategy.

        Returns:
            TradingStrategy: The trading strategy implementation.
        """
        return self._strategy

    @strategy.setter
    def strategy(self, value: TradingStrategy) -> None:
        """
        Set the trading strategy.

        Args:
            value (TradingStrategy): The trading strategy implementation.
        """
        self._strategy = value

    @property
    def data_manager(self) -> DataManager:
        """
        Get the data manager.

        Returns:
            DataManager: The data manager instance.
        """
        return self._data_manager

    @data_manager.setter
    def data_manager(self, value: DataManager) -> None:
        """
        Set the data manager.

        Args:
            value (DataManager): The data manager instance.
        """
        self._data_manager = value

    def configure_settings(
        self,
        api_key: str,
        secret: str,
        pair: str,
        capital: float,
        strategy_params: Dict[str, Any],
    ) -> None:
        """
        Configure all bot settings and parameters.

        Allows the user to set API credentials (through console or GUI),
        select the trading pair, define capital, and configure strategy parameters.

        Args:
            api_key (str): Binance API key.
            secret (str): Binance secret key.
            pair (str): The trading pair symbol (e.g., 'BTCUSDT').
            capital (float): Initial capital in USDT.
            strategy_params (dict): Strategy-specific parameters.
        """
        pass

    def start_bot(self) -> None:
        """
        Start the trading bot.

        Initializes all components and begins the main trading loop,
        preparing the bot to execute trading signals.
        """
        pass

    def stop_bot(self) -> None:
        """
        Stop the trading bot.

        Gracefully stops the trading loop and finalizes any pending operations,
        ensuring clean shutdown of all components.
        """
        pass

    def run_loop(self) -> None:
        """
        Execute the main trading loop.

        Contains the core logic that repeatedly:
        1. Calls the API to fetch current market data
        2. Verifies the trading strategy for signals
        3. Executes buy/sell orders via the portfolio manager
        4. Updates status information

        This loop continues until the bot is stopped.
        """
        pass

    def display_status(self) -> None:
        """
        Display real-time bot status information.

        Shows the current portfolio balance, portfolio value in USDT,
        active trading pair, strategy status, and recent trades to the user
        via console output or GUI.
        """
        pass
