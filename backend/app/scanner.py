from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from .models import now_iso
from .strategy import build_trade_idea

class MarketScanner:
    def __init__(self, symbols: list[str]) -> None:
        self.symbols = symbols
        self.candles: dict[str, list[dict[str, float]]] = defaultdict(list)
        self.latest: dict[str, dict[str, Any]] = {}
        self.signals: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def update(self, symbol: str, candle: dict[str, float], pcr: float | None = None) -> dict[str, Any]:
        async with self._lock:
            candles = self.candles[symbol]
            candles.append(candle)
            self.candles[symbol] = candles[-100:]
            signal = build_trade_idea(symbol, self.candles[symbol], pcr)
            snapshot = {"symbol": symbol, "candle": candle, "signal": signal, "updated_at": now_iso()}
            self.latest[symbol] = snapshot
            if signal:
                self.signals.append(signal)
                self.signals = self.signals[-500:]
            return snapshot

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return {"symbols": self.latest, "signals": list(self.signals)}
