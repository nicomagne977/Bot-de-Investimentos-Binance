"""
Portfolio management module for simulated trading.

This module handles paper trading simulation and trade history persistence,
tracking balances and managing buy/sell operations.
"""

from typing import List, Dict, Any
import json
from datetime import datetime


class Portfolio:
    """
    Manages paper trading (simulated trading) and trade history persistence.

    This class simulates a trading portfolio by tracking USDT balance and
    cryptocurrency holdings separately. It records all transactions and
    provides methods for calculating portfolio value.

    Attributes:
        _usdt_balance (float): Current balance in USDT (fiat currency).
        _crypto_balance (float): Current balance in cryptocurrency (e.g., BTC).
        _trade_history (list): List of all executed trades for record-keeping.
    """

    def __init__(self, initial_capital: float) -> None:
        """
        Initialize the Portfolio with an initial capital amount.

        Args:
            initial_capital (float): The starting capital in USDT.
        """
        self._usdt_balance = initial_capital
        self._crypto_balance = 0.0
        self._trade_history = []

    @property
    def usdt_balance(self) -> float:
        """
        Get the current USDT balance.

        Returns:
            float: The current USDT balance.
        """
        return self._usdt_balance

    @usdt_balance.setter
    def usdt_balance(self, value: float) -> None:
        """
        Set the USDT balance.

        Args:
            value (float): The new USDT balance.
        """
        self._usdt_balance = value

    @property
    def crypto_balance(self) -> float:
        """
        Get the current cryptocurrency balance.

        Returns:
            float: The current cryptocurrency balance (e.g., BTC quantity).
        """
        return self._crypto_balance

    @crypto_balance.setter
    def crypto_balance(self, value: float) -> None:
        """
        Set the cryptocurrency balance.

        Args:
            value (float): The new cryptocurrency balance.
        """
        self._crypto_balance = value

    @property
    def trade_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete trade history.

        Returns:
            list: A list of all executed trades.
        """
        return self._trade_history

    @trade_history.setter
    def trade_history(self, value: List[Dict[str, Any]]) -> None:
        """
        Set the trade history.

        Args:
            value (list): The new trade history list.
        """
        self._trade_history = value

    def update_balance(self, price: float, quantity: float, side: str) -> None:
        """
        Update portfolio balances based on a trade.

        Updates both USDT and cryptocurrency balances depending on whether
        a buy or sell operation was executed.

        Args:
            price (float): The price per unit of cryptocurrency.
            quantity (float): The quantity of cryptocurrency traded.
            side (str): The side of the trade - 'BUY' or 'SELL'.
        """
        side = side.upper()
        timestamp = datetime.utcnow().isoformat() + "Z"
        if side == "BUY":
            cost = price * quantity
            self._usdt_balance -= cost
            self._crypto_balance += quantity
            trade = {
                "side": "BUY",
                "price": price,
                "quantity": quantity,
                "cost": cost,
                "timestamp": timestamp,
            }
            self._trade_history.append(trade)
        elif side == "SELL":
            proceeds = price * quantity
            self._crypto_balance -= quantity
            self._usdt_balance += proceeds
            trade = {
                "side": "SELL",
                "price": price,
                "quantity": quantity,
                "proceeds": proceeds,
                "timestamp": timestamp,
            }
            self._trade_history.append(trade)
        else:
            raise ValueError("side must be 'BUY' or 'SELL'")

    def execute_buy(self, price: float) -> float:
        """
        Execute a buy order using all available USDT.

        Simulates buying cryptocurrency with all available capital at the given price.

        Args:
            price (float): The current price of the cryptocurrency.

        Returns:
            float: The quantity of cryptocurrency purchased.
        """
        if price <= 0:
            return 0.0
        if self._usdt_balance <= 0:
            return 0.0

        quantity = self._usdt_balance / price
        # update balances and record trade
        self.update_balance(price=price, quantity=quantity, side="BUY")
        return quantity

    def execute_sell(self, price: float) -> float:
        """
        Execute a sell order of all cryptocurrency holdings.

        Simulates selling all held cryptocurrency at the given price
        and converting to USDT.

        Args:
            price (float): The current price of the cryptocurrency.

        Returns:
            float: The amount of USDT received from the sale.
        """
        if price <= 0:
            return 0.0
        if self._crypto_balance <= 0:
            return 0.0

        quantity = self._crypto_balance
        proceeds = quantity * price
        self.update_balance(price=price, quantity=quantity, side="SELL")
        return proceeds

    def get_total_value_usdt(self, current_price: float) -> float:
        """
        Calculate the total portfolio value in USDT.

        Computes the total portfolio value by adding USDT balance to the
        current value of cryptocurrency holdings at the given price.
        This is used for display and performance tracking.

        Args:
            current_price (float): The current price of the cryptocurrency.

        Returns:
            float: The total portfolio value in USDT.
        """
        return self._usdt_balance + (self._crypto_balance * current_price)

    def save_trades_to_file(self, filename: str) -> None:
        """
        Save all trade history to a file.

        Records all executed transactions to a file (JSON or CSV format)
        for later analysis and record-keeping. This is a required functional
        requirement for maintaining trading history.

        Args:
            filename (str): The path and filename where trades will be saved.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({"trades": self._trade_history}, f, indent=2)
        except Exception:
            raise
