from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .fyers import FyersClient
from .scanner import MarketScanner
from .ws import hub

app = FastAPI(title=settings.app_name, version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
fyers = FyersClient()
scanner = MarketScanner(["NIFTY50", "BANKNIFTY", "RELIANCE", "TCS", "INFY", "HDFCBANK"])

@app.on_event("startup")
async def startup():
    import asyncio
    asyncio.create_task(__import__("app.ws", fromlist=["heartbeat"]).heartbeat())

@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment, "live_trading_enabled": settings.live_trading_enabled, "fyers_configured": bool(settings.fyers_client_id and settings.fyers_access_token)}

@app.get("/api/fyers/login")
async def fyers_login():
    return {"url": fyers.login_url()}

@app.get("/api/config")
async def config():
    return {"app": settings.app_name, "live_trading_enabled": settings.live_trading_enabled, "symbols": scanner.symbols}

@app.get("/api/scanner")
async def scanner_snapshot():
    return await scanner.snapshot()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await hub.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        hub.disconnect(ws)
