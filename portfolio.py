"""Portfolio Management Module  """

import json
import csv
from typing import Dict, Any
from datetime import datetime
from decimal import Decimal


class Portfolio:
    """
    Simple simulated portfolio: tracks USDT balance and asset balance (e.g., BTC).
    Trades are logged to trades.json and trades.csv.
    """

    def __init__(self, initial_usdt: float, asset_symbol: str = "BTC"):
        self.usdt = float(initial_usdt)
        self.asset = 0.0
        self.asset_symbol = asset_symbol.upper()
        self.trades = []  # in-memory record

        self.csv_file = "trades.csv"
        self.json_file = "trades.json"

        # ensure files exist with header if csv missing
        try:
            with open(self.csv_file, 'x', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp','type','price','quantity','asset','usdt_after','asset_after'])
                writer.writeheader()
        except FileExistsError:
            pass

        try:
            with open(self.json_file, 'x') as f:
                json.dump([], f)
        except FileExistsError:
            pass

    def _record_trade(self, t: Dict[str, Any]) -> None:
        # append to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp','type','price','quantity','asset','usdt_after','asset_after'])
            writer.writerow({
                'timestamp': t['timestamp'],
                'type': t['type'],
                'price': t['price'],
                'quantity': t['quantity'],
                'asset': self.asset_symbol,
                'usdt_after': t['usdt_after'],
                'asset_after': t['asset_after']
            })
        # append to JSON
        with open(self.json_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data.append(t)
            f.seek(0)
            json.dump(data, f, indent=2)
        self.trades.append(t)

    def buy_all_in(self, price: float) -> Dict[str, Any]:
        """
        Use all USDT to buy asset at given price. Returns trade dict.
        """
        if self.usdt <= 0:
            raise RuntimeError("No USDT to buy with")
        quantity = self.usdt / price
        # update balances
        self.asset += quantity
        self.usdt = 0.0

        t = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'BUY',
            'price': price,
            'quantity': quantity,
            'usdt_after': self.usdt,
            'asset_after': self.asset
        }
        self._record_trade(t)
        return t

    def sell_all(self, price: float) -> Dict[str, Any]:
        """
        Sell all asset at given price, convert to USDT.
        """
        if self.asset <= 0:
            raise RuntimeError("No asset to sell")
        quantity = self.asset
        proceeds = quantity * price
        self.usdt += proceeds
        self.asset = 0.0

        t = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'SELL',
            'price': price,
            'quantity': quantity,
            'usdt_after': self.usdt,
            'asset_after': self.asset
        }
        self._record_trade(t)
        return t

    def portfolio_value(self, current_price: float) -> float:
        """
        Return total portfolio value in USDT (usdt + asset*price).
        """
        return self.usdt + self.asset * current_price
