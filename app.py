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
import threading
import time
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk
except Exception:
    tk = None
    ttk = None


class LiveWindow:
    """
    Simple tkinter window that displays live price and basic historical info.

    The window runs in its own thread. It polls the provided BinanceClient
    for the current price at the given `update_interval` (seconds) and updates
    the UI labels. The historical data is fetched once on start to display
    a brief summary.
    """

    def __init__(
        self,
        client: BinanceClient,
        pair: str,
        portfolio: Optional[Portfolio] = None,
        update_interval: int = 60,
    ):
        self.client = client
        self.pair = pair
        self.portfolio = portfolio
        self.update_interval = 20
        self._thread = None
        self._stop_event = threading.Event()
        self._root = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        # If tkinter is not available, raise
        if tk is None:
            return

        self._root = tk.Tk()
        self._root.title(f"Live price - {self.pair}")

        # UI layout
        frm = ttk.Frame(self._root, padding=12)
        frm.grid()

        ttk.Label(frm, text=f"Pair:").grid(column=0, row=0, sticky="w")
        self._pair_lbl = ttk.Label(frm, text=self.pair, font=(None, 12, "bold"))
        self._pair_lbl.grid(column=1, row=0, sticky="w")

        ttk.Label(frm, text="Current Price:").grid(column=0, row=1, sticky="w")
        self._price_lbl = ttk.Label(frm, text="-", font=(None, 14))
        self._price_lbl.grid(column=1, row=1, sticky="w")

        ttk.Label(frm, text="Last Update:").grid(column=0, row=2, sticky="w")
        self._update_lbl = ttk.Label(frm, text="-")
        self._update_lbl.grid(column=1, row=2, sticky="w")

        ttk.Separator(frm, orient="horizontal").grid(
            column=0, row=3, columnspan=2, pady=8, sticky="ew"
        )

        ttk.Label(frm, text="Last Close:").grid(column=0, row=4, sticky="w")
        self._lastclose_lbl = ttk.Label(frm, text="-")
        self._lastclose_lbl.grid(column=1, row=4, sticky="w")
        # Balances
        ttk.Label(frm, text="USDT Balance:").grid(column=0, row=5, sticky="w")
        self._usdt_lbl = ttk.Label(frm, text="-")
        self._usdt_lbl.grid(column=1, row=5, sticky="w")

        ttk.Label(frm, text="Crypto Balance:").grid(column=0, row=6, sticky="w")
        self._crypto_lbl = ttk.Label(frm, text="-")
        self._crypto_lbl.grid(column=1, row=6, sticky="w")

        # Trade history area
        ttk.Label(frm, text="Trade History:").grid(column=0, row=5, sticky="nw")
        self._history_box = tk.Text(frm, width=40, height=8, wrap="none")
        self._history_box.grid(column=0, row=6, columnspan=2, pady=(6, 0))
        self._history_box.insert("1.0", "No trades yet.\n")
        self._history_box.config(state="disabled")

        # fetch historical data once
        try:
            df = self.client.fetch_historical_data(self.pair, "1m")
            if df is not None and len(df) > 0:
                last_close = df.iloc[-1]["close"]
                self._lastclose_lbl.config(text=f"{last_close:.8f}")
        except Exception:
            pass

        # schedule updates
        self._schedule_update()

        # start tkinter mainloop
        try:
            self._root.mainloop()
        except Exception:
            pass

    def _schedule_update(self) -> None:
        if self._stop_event.is_set():
            if self._root:
                try:
                    self._root.destroy()
                except Exception:
                    pass
            return

        # perform update
        try:
            price = self.client.get_current_price(self.pair)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if hasattr(self, "_price_lbl") and self._price_lbl:
                try:
                    # compute change since last update
                    prev = getattr(self, "_last_price", None)
                    change_text = ""
                    if prev is not None and prev > 0:
                        diff = price - prev
                        pct = (diff / prev) * 100
                        change_text = f"  (Δ {diff:.8f} | {pct:+.3f}%)"
                    self._price_lbl.config(text=f"{price:.8f}{change_text}")
                    self._update_lbl.config(text=ts)
                    self._last_price = price
                except Exception:
                    pass
        except Exception:
            pass

        # update trade history display from portfolio
        try:
            if self.portfolio is not None and hasattr(self, "_history_box"):
                trades = list(self.portfolio.trade_history)
                self._history_box.config(state="normal")
                self._history_box.delete("1.0", "end")
                if trades:
                    for t in trades[-50:]:
                        line = f"{t.get('timestamp','')}: {t.get('side')} {t.get('quantity'):.8f} @ {t.get('price'):.8f}\n"
                        self._history_box.insert("end", line)
                else:
                    self._history_box.insert("1.0", "No trades yet.\n")
                self._history_box.config(state="disabled")
                # update balances display
                try:
                    self._usdt_lbl.config(
                        text=f"{self.portfolio.usdt_balance:.2f} USDT"
                    )
                    self._crypto_lbl.config(text=f"{self.portfolio.crypto_balance:.8f}")
                except Exception:
                    pass
        except Exception:
            pass

        # call again after update_interval seconds
        if self._root:
            try:
                self._root.after(self.update_interval * 1000, self._schedule_update)
            except Exception:
                pass

    def stop(self) -> None:
        self._stop_event.set()
        # close the tkinter window from its thread
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass


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
        if self._is_running:
            print("Bot is already running.")
            return

        if not self._binance_client:
            print(
                "Error: Binance client is not configured. Call configure_settings() first."
            )
            return

        if not self._pair:
            print("Error: Trading pair is not set.")
            return

        # mark running
        self._is_running = True

        # Start live GUI window if tkinter is available
        if tk is not None:
            try:
                self._live_window = LiveWindow(
                    self._binance_client, self._pair, self._portfolio
                )
                self._live_window.start()
            except Exception as e:
                print(f"Could not start live window: {e}")
        else:
            print(
                "tkinter not available; live window disabled. Using console updates instead."
            )

        # start background run loop for non-GUI tasks
        self._run_thread = threading.Thread(target=self.run_loop, daemon=True)
        self._run_thread.start()
        print("Bot started.")

    def buy_all(self) -> None:
        """
        Attempt to buy with all available USDT balance.

        Verifies the portfolio has USDT available, fetches current price,
        simulates a buy through the BinanceClient (test order), and updates
        the Portfolio balances accordingly.
        """
        if not self._portfolio:
            print("Portfolio not initialized.")
            return
        usdt = self._portfolio.usdt_balance
        if usdt <= 0:
            print("No USDT available to buy.")
            return
        price = (
            self._binance_client.get_current_price(self._pair)
            if self._binance_client
            else 0.0
        )
        if price <= 0:
            print("Could not fetch price for buying.")
            return

        qty = usdt / price
        # verify app-side balance before placing simulated order
        if qty <= 0:
            print("Calculated zero quantity; aborting buy.")
            return

        order = (
            self._binance_client.test_buy(self._pair, qty, price)
            if self._binance_client
            else None
        )
        # apply to portfolio (simulate execution)
        purchased_qty = self._portfolio.execute_buy(price)
        print(f"Bought {purchased_qty:.8f} {self._pair} at {price:.8f} (simulated)")

    def sell_all(self) -> None:
        """
        Attempt to sell all cryptocurrency holdings.

        Verifies the portfolio has crypto available, fetches current price,
        simulates a sell via BinanceClient and updates the Portfolio balances.
        """
        if not self._portfolio:
            print("Portfolio not initialized.")
            return
        crypto = self._portfolio.crypto_balance
        if crypto <= 0:
            print("No crypto available to sell.")
            return
        price = (
            self._binance_client.get_current_price(self._pair)
            if self._binance_client
            else 0.0
        )
        if price <= 0:
            print("Could not fetch price for selling.")
            return

        order = (
            self._binance_client.test_sell(self._pair, crypto, price)
            if self._binance_client
            else None
        )
        proceeds = self._portfolio.execute_sell(price)
        print(f"Sold {crypto:.8f} {self._pair} for {proceeds:.2f} USDT (simulated)")

    def stop_bot(self) -> None:
        """
        Stop the trading bot.

        Gracefully stops the trading loop and finalizes any pending operations,
        ensuring clean shutdown of all components.
        """
        if not self._is_running:
            print("Bot is not running.")
            return
        print("Stopping bot...")
        self._is_running = False

        # stop live window if present
        if hasattr(self, "_live_window") and self._live_window is not None:
            try:
                self._live_window.stop()
            except Exception:
                pass

        # wait briefly for thread to terminate
        if hasattr(self, "_run_thread") and self._run_thread.is_alive():
            self._run_thread.join(timeout=5)
        print("Bot stopped.")

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
        # Fetch historical data once at start (optional)
        try:
            if self._binance_client and self._pair:
                _ = self._binance_client.fetch_historical_data(self._pair, "1m")
        except Exception:
            pass

        # Background loop - reserved for non-GUI periodic tasks
        while self._is_running:
            # Currently GUI handles price display. Sleep and check is_running
            for _ in range(60):
                if not self._is_running:
                    break
                time.sleep(1)

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
            print("  2) Buy with all USDT (simulated)")
            print("  3) Sell all crypto (simulated)")
            print("  4) Stop bot")
            print("  5) Exit program")
            print("=" * 40)
            choice = input("Choose an action (1-5): ").strip()

            if choice == "1":
                print("Starting the bot...")
                try:
                    self.start_bot()
                except Exception as e:
                    print(f"Error when starting bot: {e}")
            elif choice == "2":
                try:
                    self.buy_all()
                except Exception as e:
                    print(f"Buy failed: {e}")
            elif choice == "3":
                try:
                    self.sell_all()
                except Exception as e:
                    print(f"Sell failed: {e}")
            elif choice == "4":
                try:
                    self.stop_bot()
                except Exception as e:
                    print(f"Stop failed: {e}")
            elif choice == "5":
                print("Exiting program. Goodbye.")
                # ensure bot stopped
                if self._is_running:
                    self.stop_bot()
                break
            else:
                print("Invalid choice, please enter 1-5.")


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
