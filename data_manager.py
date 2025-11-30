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

        # Create file if it does not exist
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                json.dump([], f, indent=4)

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
            with open(self.json_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Fix corrupted JSON file by resetting it
            with open(self.json_path, "w") as f:
                json.dump([], f, indent=4)
            return []
        except FileNotFoundError:
            # Recreate file if deleted
            with open(self.json_path, "w") as f:
                json.dump([], f, indent=4)
            return []

    # ----------------------------------------------------------------------

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """
        Save data to the JSON file.

        Args:
            data (list): List of dictionaries to write.
        """
        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4)

    # ----------------------------------------------------------------------

    def append_trade(self, trade: Dict[str, Any]) -> None:
        """
        Add one trade entry into the JSON file.

        Args:
            trade (dict): A single trade record.
        """
        data = self.load_data()
        data.append(trade)
        self.save_data(data)
