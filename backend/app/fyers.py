from __future__ import annotations

import json
from typing import Any
import httpx

from .config import settings

FYERS_AUTH_URL = "https://api-t1.fyers.in/api/v3/generate-authcode"
FYERS_TOKEN_URL = "https://api-t1.fyers.in/api/v3/validate-authcode"

class FyersClient:
    def __init__(self) -> None:
        self.access_token = settings.fyers_access_token

    def login_url(self, state: str = "mahadev") -> str:
        params = {
            "client_id": settings.fyers_client_id,
            "redirect_uri": settings.fyers_redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return str(httpx.URL(FYERS_AUTH_URL, params=params))

    async def exchange_auth_code(self, auth_code: str) -> dict[str, Any]:
        payload = {
            "grant_type": "authorization_code",
            "appIdHash": settings.fyers_secret_key,
            "code": auth_code,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(FYERS_TOKEN_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token", self.access_token)
            return data

    async def history(self, symbol: str, resolution: str = "15", range_from: str = "2026-01-01", range_to: str = "2026-01-02") -> dict[str, Any]:
        if not self.access_token:
            raise RuntimeError("FYERS_ACCESS_TOKEN is not configured")
        url = "https://api-t1.fyers.in/data/history"
        payload = {"symbol": symbol, "resolution": resolution, "date_format": "1", "range_from": range_from, "range_to": range_to, "cont_flag": "1"}
        headers = {"Authorization": f"{settings.fyers_client_id}:{self.access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=payload, headers=headers)
            response.raise_for_status()
            return response.json()
