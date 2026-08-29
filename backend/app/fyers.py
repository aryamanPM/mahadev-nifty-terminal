from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import httpx
from fyers_apiv3.FyersWebsocket import data_ws

from .config import settings

FYERS_AUTH_URL = "https://api-t1.fyers.in/api/v3/generate-authcode"
FYERS_TOKEN_URL = "https://api-t1.fyers.in/api/v3/validate-authcode"

class FyersClient:
    def __init__(self) -> None:
        self.access_token = settings.fyers_access_token
        self.ws: data_ws.FyersDataSocket | None = None
        self._ws_task: asyncio.Task | None = None

    def login_url(self, state: str = "mahadev") -> str:
        params = {"client_id": settings.fyers_client_id, "redirect_uri": settings.fyers_redirect_uri, "response_type": "code", "state": state}
        return str(httpx.URL(FYERS_AUTH_URL, params=params))

    async def exchange_auth_code(self, auth_code: str) -> dict[str, Any]:
        # FYERS expects appIdHash = SHA-256(app_id + secret) in the auth-code flow.
        import hashlib
        app_id_hash = hashlib.sha256(f"{settings.fyers_client_id}{settings.fyers_secret_key}".encode()).hexdigest()
        payload = {"grant_type": "authorization_code", "appIdHash": app_id_hash, "code": auth_code}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(FYERS_TOKEN_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token", self.access_token)
            return data

    async def history(self, symbol: str, resolution: str = "15", range_from: str | None = None, range_to: str | None = None) -> dict[str, Any]:
        if not self.access_token:
            raise RuntimeError("FYERS_ACCESS_TOKEN is not configured")
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=10)
        url = "https://api-t1.fyers.in/data/history"
        payload = {"symbol": symbol, "resolution": resolution, "date_format": "1", "range_from": range_from or start.isoformat(), "range_to": range_to or end.isoformat(), "cont_flag": "1"}
        headers = {"Authorization": f"{settings.fyers_client_id}:{self.access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def connect_market_data(self, symbols: list[str], on_tick: Callable[[dict], Any]) -> None:
        if not self.access_token:
            raise RuntimeError("FYERS_ACCESS_TOKEN is not configured")
        loop = asyncio.get_running_loop()
        ready = loop.create_future()

        def on_message(message):
            result = on_tick(message)
            if asyncio.iscoroutine(result):
                asyncio.run_coroutine_threadsafe(result, loop)

        def on_error(message):
            if not ready.done():
                ready.set_exception(RuntimeError(f"FYERS websocket error: {message}"))

        def on_close(message):
            if not ready.done():
                ready.set_exception(RuntimeError(f"FYERS websocket closed: {message}"))

        self.ws = data_ws.FyersDataSocket(
            access_token=f"{settings.fyers_client_id}:{self.access_token}",
            log_path=".",
            litemode=False,
            write_to_file=False,
            reconnect=True,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        def run_socket():
            self.ws.connect()
            self.ws.subscribe(symbols=symbols, data_type="symbolData")
            if not ready.done():
                loop.call_soon_threadsafe(ready.set_result, True)

        self._ws_task = asyncio.create_task(asyncio.to_thread(run_socket))
        await ready
