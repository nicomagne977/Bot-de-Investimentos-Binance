"""
Data management module for JSON data persistence.

This module handles loading and saving application data in JSON format,
managing all data storage and retrieval operations.
"""

import json
import os
from typing import Any, Dict, List


class DataManager:
    """
    Class responsible for saving and loading data (trades, config, etc.)
    to/from a JSON file.

    Attributes:
        json_path (str): Path to the JSON file where data will be stored.
    """

    def __init__(self, json_path: str = "trades.json"):
        """
        Initialize the DataManager with a default path.

        Args:
            json_path (str): Path to the JSON file.
        """
        self.json_path = json_path

        # Create file if it does not exist, initialize as structured state
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"trades": [], "usdt_balance": None, "crypto_balance": None},
                    f,
                    indent=4,
                )

    # ----------------------------------------------------------------------

    def set_json_path(self, path: str) -> None:
        """
        Update the JSON file path.

        Args:
            path (str): New path to the JSON file.
        """
        self.json_path = path

        # Auto-create file if missing
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                json.dump([], f, indent=4)

    # ----------------------------------------------------------------------

    def load_data(self) -> List[Dict[str, Any]]:
        """
        Load data from the JSON file.

        Returns:
            list: The list of stored operations (or any JSON content).
        """
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Fix corrupted JSON file by resetting it
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"trades": [], "usdt_balance": None, "crypto_balance": None},
                    f,
                    indent=4,
                )
            return {"trades": [], "usdt_balance": None, "crypto_balance": None}
        except FileNotFoundError:
            # Recreate file if deleted
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"trades": [], "usdt_balance": None, "crypto_balance": None},
                    f,
                    indent=4,
                )
            return {"trades": [], "usdt_balance": None, "crypto_balance": None}

    # ----------------------------------------------------------------------

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Save data to the JSON file.

        Args:
            data (list): List of dictionaries to write.
        """
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ----------------------------------------------------------------------

    def append_trade(self, trade: Dict[str, Any]) -> None:
        """
        Add one trade entry into the JSON file.

        Args:
            trade (dict): A single trade record.
        """
        state = self.load_data()
        # If the file stored a list previously, convert to structured state
        if isinstance(state, list):
            state = {"trades": state, "usdt_balance": None, "crypto_balance": None}
        trades = state.get("trades") or []
        trades.append(trade)
        state["trades"] = trades
        self.save_data(state)

    # ------------------------------------------------------------------

    def charge_data(self) -> Dict[str, Any]:
        """
        Return structured state from the JSON file.

        Returns a dict with keys: 'trades' (list), 'usdt_balance' (float|None),
        'crypto_balance' (float|None).
        """
        state = self.load_data()
        # Normalize to structured dict
        if isinstance(state, list):
            return {"trades": state, "usdt_balance": None, "crypto_balance": None}
        # Ensure keys exist
        return {
            "trades": state.get("trades", []),
            "usdt_balance": state.get("usdt_balance"),
            "crypto_balance": state.get("crypto_balance"),
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        Save a structured state dict to the JSON file.

        Expected keys: 'trades', 'usdt_balance', 'crypto_balance'.
        """
        # Normalize
        out = {
            "trades": state.get("trades", []),
            "usdt_balance": state.get("usdt_balance"),
            "crypto_balance": state.get("crypto_balance"),
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=4)
