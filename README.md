# Mahadev Nifty Terminal

Live Indian-market research and signal terminal built around FYERS market data.

## Status

Initial repository scaffold. The production implementation will keep live order execution disabled until FYERS authentication, static-IP requirements, risk controls, and paper-trading validation are configured.

## Planned architecture

- FastAPI async backend
- FYERS REST/WebSocket market-data adapter
- Real OHLCV aggregation and indicators
- Technical, Smart Money, and derivatives agents
- Risk/reward and signal engine
- PostgreSQL journal and analytics
- React dashboard with WebSocket updates
- Paper trading first; explicit live-order gate
- Docker/Railway deployment

## Important

The original prototype used random prices, RSI, PCR, ATR, and FVG flags. Those are simulation values and are not suitable for live trading. The live implementation must calculate indicators from actual market data and derive performance statistics from recorded/backtested outcomes rather than using the prototype's hard-coded 71.4% projection.
