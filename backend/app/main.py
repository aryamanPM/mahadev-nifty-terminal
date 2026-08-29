from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .fyers import FyersClient

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
fyers = FyersClient()

@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment, "live_trading_enabled": settings.live_trading_enabled, "fyers_configured": bool(settings.fyers_client_id and settings.fyers_access_token)}

@app.get("/api/fyers/login")
async def fyers_login():
    return {"url": fyers.login_url()}

@app.get("/api/config")
async def config():
    return {"app": settings.app_name, "live_trading_enabled": settings.live_trading_enabled}
