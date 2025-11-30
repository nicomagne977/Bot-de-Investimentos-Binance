"""
Main application module for the Binance trading bot.

This module contains the primary orchestrator class that manages all components
of the trading bot including configuration, execution, and real-time status display.
"""

from typing import Optional, Dict, Any
import json
from pathlib import Path
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
        _pair (str): The trading pair symbol (e.g., 'BTCUSDT'). TODO : use more than one??,
        _capital (float): The initial capital allocated for trading in USDT. TODO : maybe put it into the portfiolio class?
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
        # Configure the Binance client with API credentials
        self._binance_client = BinanceClient(
            api_key=api_key, secret_key=secret, testnet=True  # Using testnet for safety
        )

        # Set trading pair and capital
        self._pair = pair
        self._capital = capital

        # Initialize portfolio with the initial capital
        self._portfolio = Portfolio(initial_capital=capital)

        # Initialize the trading strategy (MovingAverageStrategy)
        from moving_average_strategy import MovingAverageStrategy

        short_window = strategy_params.get("short_window", 10)
        long_window = strategy_params.get("long_window", 30)

        self._strategy = MovingAverageStrategy(
            short_window=short_window, long_window=long_window
        )

        # Configure data manager
        json_filename = strategy_params.get("json_path", "trading_data.json")

        # Ensure JSON data file exists in the current working directory and use a relative path
        data_file = Path(json_filename)
        if not data_file.exists():
            try:
                data_file.write_text(json.dumps({"trades": []}, indent=2))
                print(f"Created data file: {data_file}")
            except Exception as e:
                print(f"Warning: could not create data file '{data_file}': {e}")

        # Configure DataManager with the (relative) path
        self._data_manager.set_json_path(str(data_file))

        print(f"\n✓ Bot configuration completed successfully!")
        print(f"  Trading Pair: {self._pair}")
        print(f"  Initial Capital: ${self._capital:.2f} USDT")
        print(
            f"  Strategy: Moving Average (Short: {short_window}, Long: {long_window})"
        )
        print(f"  Mode: Testnet")

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

    def collect_user_input(self) -> Dict[str, Any]:
        """
        Collect all necessary configuration data from the user.

        Interactively prompts the user to enter API credentials, trading pair,
        capital amount, strategy parameters, and data storage path. Validates
        all inputs and returns them as a dictionary ready for configure_settings().

        Returns:
            dict: A dictionary containing:
                - api_key (str): Binance API key
                - secret (str): Binance secret key
                - pair (str): Trading pair symbol
                - capital (float): Initial capital in USDT
                - strategy_params (dict): Strategy parameters
        """
        print("=" * 60)
        print("          BINANCE TRADING BOT - CONFIGURATION")
        print("=" * 60)

        # [1/5] Collect API credentials
        print("\n[1/5] API Configuration")
        print("-" * 60)
        api_key = input("Enter your Binance API Key: ").strip()
        secret_key = input("Enter your Binance Secret Key: ").strip()

        # [2/5] Collect trading pair
        print("\n[2/5] Trading Pair Selection")
        print("-" * 60)
        trading_pair = input("Enter the trading pair (e.g., BTCUSDT): ").strip().upper()

        # [3/5] Collect capital with validation
        print("\n[3/5] Capital Configuration")
        print("-" * 60)
        while True:
            try:
                capital = float(
                    input("Enter the initial capital in USDT (minimum $10): ")
                )
                if capital < 10:
                    print("Error: Capital must be at least $10. Please try again.")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid number.")

        # [4/5] Collect strategy parameters
        print("\n[4/5] Strategy Parameters (Moving Average)")
        print("-" * 60)
        while True:
            try:
                short_window = int(
                    input("Enter the short-term moving average period (default: 10): ")
                    or "10"
                )
                if short_window <= 0:
                    print("Error: Period must be a positive number.")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid integer.")

        while True:
            try:
                long_window = int(
                    input("Enter the long-term moving average period (default: 30): ")
                    or "30"
                )
                if long_window <= 0 or long_window <= short_window:
                    print(
                        "Error: Long window must be positive and greater than short window."
                    )
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid integer.")

        # Data storage: use a relative default file name `json.data` in current directory
        json_path = "json.data"

        # Prepare strategy parameters dictionary
        strategy_params = {
            "short_window": short_window,
            "long_window": long_window,
            "json_path": json_path,
        }

        # Return all configuration data
        return {
            "api_key": api_key,
            "secret": secret_key,
            "pair": trading_pair,
            "capital": capital,
            "strategy_params": strategy_params,
        }

    def action_menu(self) -> None:
        """
        Interactive action menu loop for the user.

        Presents a small menu of actions the user can perform. For now the menu
        supports two actions:
            1) Start bot - calls `start_bot()`
            2) Exit program - breaks the loop and returns to the caller

        This method keeps prompting until the user chooses to exit.
        """
        while True:
            print("\n" + "=" * 40)
            print("Available actions:")
            print("  1) Start bot")
            print("  2) Exit program")
            print("=" * 40)
            choice = input("Choose an action (1-2): ").strip()

            if choice == "1":
                print("Starting the bot...")
                try:
                    self.start_bot()
                except Exception as e:
                    print(f"Error when starting bot: {e}")
            elif choice == "2":
                print("Exiting program. Goodbye.")
                break
            else:
                print("Invalid choice, please enter 1 or 2.")


def main() -> None:
    """Main entry point for the trading bot application."""
    app = App()

    # Collect user input through the dedicated method
    config_data = app.collect_user_input()

    # Configure the bot with the collected data
    print("\n" + "=" * 60)
    app.configure_settings(
        api_key=config_data["api_key"],
        secret=config_data["secret"],
        pair=config_data["pair"],
        capital=config_data["capital"],
        strategy_params=config_data["strategy_params"],
    )
    print("=" * 60)
    # Launch interactive action menu
    app.action_menu()


if __name__ == "__main__":
    main()
