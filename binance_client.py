"""
BinanceClient module for managing API communication with Binance.

This class handles all API operations for fetching price data and market information
from the Binance exchange, supporting both testnet and live trading environments.
"""

from typing import Optional
import requests
import pandas as pd
from datetime import datetime


class BinanceClient:
    """
    Manages exclusive communication with the Binance API.

    This class is responsible for authenticating with Binance using API credentials
    and retrieving market data such as historical prices and current price information.
    Supports both testnet and live trading modes.

    Attributes:
        _api_key (str): The API key for authenticating with Binance.
        _secret_key (str): The secret key for signing API requests.
        _testnet (bool): Flag indicating whether to use testnet or live trading.
    """

    def __init__(self, api_key: str, secret_key: str, testnet: bool = True) -> None:
        """
        Initialize the BinanceClient with API credentials.

        Args:
            api_key (str): The API key for Binance authentication.
            secret_key (str): The secret key for Binance authentication.
            testnet (bool): Whether to use testnet mode (default: True).
        """
        self._api_key = api_key
        self._secret_key = secret_key
        self._testnet = testnet

    @property
    def api_key(self) -> str:
        """
        Get the API key.

        Returns:
            str: The API key used for authentication.
        """
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        """
        Set the API key.

        Args:
            value (str): The new API key.
        """
        self._api_key = value

    @property
    def secret_key(self) -> str:
        """
        Get the secret key.

        Returns:
            str: The secret key used for signing requests.
        """
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value: str) -> None:
        """
        Set the secret key.

        Args:
            value (str): The new secret key.
        """
        self._secret_key = value

    @property
    def testnet(self) -> bool:
        """
        Get the testnet mode flag.

        Returns:
            bool: True if using testnet, False if using live trading.
        """
        return self._testnet

    @testnet.setter
    def testnet(self, value: bool) -> None:
        """
        Set the testnet mode flag.

        Args:
            value (bool): True for testnet mode, False for live trading.
        """
        self._testnet = value

    def fetch_historical_data(self, symbol: str, interval: str):
        """
        Fetch historical price data for a given symbol.

        Retrieves historical price data required for calculating moving averages
        and other technical indicators. The data helps in analyzing price trends
        over specific time intervals.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
            interval (str): The time interval for candlesticks (e.g., '1h', '4h', '1d').

        Returns:
            DataFrame: A pandas DataFrame containing historical price data.
        """
        base = (
            "https://testnet.binance.vision"
            if self._testnet
            else "https://api.binance.com"
        )
        url = f"{base}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": 1000}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            klines = resp.json()

            # Parse into a DataFrame
            cols = [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "num_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ]
            df = pd.DataFrame(klines, columns=cols)
            # convert numeric columns
            for c in ["open", "high", "low", "close", "volume"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            # convert timestamps
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
            return df
        except Exception:
            return None

    def get_current_price(self, symbol: str) -> float:
        """
        Get the current price of a trading pair.

        Retrieves the most recent price at regular intervals for real-time
        decision making in the trading strategy.

        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSDT').

        Returns:
            float: The current price of the symbol.
        """
        base = (
            "https://testnet.binance.vision"
            if self._testnet
            else "https://api.binance.com"
        )
        url = f"{base}/api/v3/ticker/price"
        params = {"symbol": symbol}
        try:
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            price = float(data.get("price", 0.0))
            return price
        except Exception:
            return 0.0

    def create_test_order(
        self, symbol: str, side: str, quantity: float, price: float = None
    ) -> dict:
        """
        Create a simulated test order (does not execute real trades).

        Args:
            symbol (str): Trading pair symbol
            side (str): 'BUY' or 'SELL'
            quantity (float): Quantity to buy/sell
            price (float): Price to execute at (if None, current price is used)

        Returns:
            dict: Simulated order details
        """
        side = side.upper()
        exec_price = price if price is not None else self.get_current_price(symbol)
        timestamp = datetime.utcnow().isoformat() + "Z"
        order = {
            "symbol": symbol,
            "side": side,
            "price": exec_price,
            "quantity": quantity,
            "timestamp": timestamp,
            "status": "FILLED",
        }
        return order

    def test_buy(self, symbol: str, quantity: float, price: float = None) -> dict:
        """Simulate a buy order."""
        return self.create_test_order(symbol, "BUY", quantity, price)

    def test_sell(self, symbol: str, quantity: float, price: float = None) -> dict:
        """Simulate a sell order."""
        return self.create_test_order(symbol, "SELL", quantity, price)
