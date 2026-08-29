from typing import Any


def calculate_rsi(closes: list[float], period: int = 14) -> float | None:
    if len(closes) <= period:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0.0) for d in deltas[-period:]]
    losses = [max(-d, 0.0) for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 2)


def calculate_atr(candles: list[dict[str, float]], period: int = 14) -> float | None:
    if len(candles) <= period:
        return None
    trs: list[float] = []
    for i, c in enumerate(candles):
        prev_close = candles[i - 1]["close"] if i else c["close"]
        trs.append(max(c["high"] - c["low"], abs(c["high"] - prev_close), abs(c["low"] - prev_close)))
    return round(sum(trs[-period:]) / period, 2)


def detect_fvg(candles: list[dict[str, float]]) -> dict[str, Any]:
    if len(candles) < 3:
        return {"detected": False, "direction": None}
    a, _, c = candles[-3:]
    bullish = c["low"] > a["high"]
    bearish = c["high"] < a["low"]
    if bullish:
        return {"detected": True, "direction": "BULLISH", "low": a["high"], "high": c["low"]}
    if bearish:
        return {"detected": True, "direction": "BEARISH", "low": c["high"], "high": a["low"]}
    return {"detected": False, "direction": None}


def technical_agent(candles: list[dict[str, float]]) -> dict:
    closes = [c["close"] for c in candles]
    rsi = calculate_rsi(closes)
    score = 0
    notes = []
    if rsi is not None:
        if rsi < 35:
            score += 30; notes.append(f"RSI Oversold ({rsi})")
        elif rsi > 65:
            score -= 30; notes.append(f"RSI Overbought ({rsi})")
    last = candles[-1]
    body_position = (last["close"] - last["low"]) / max(last["high"] - last["low"], 1e-9)
    if body_position > 0.7:
        score += 20; notes.append("Bullish candle positioning")
    elif body_position < 0.3:
        score -= 20; notes.append("Bearish candle positioning")
    return {"score": score, "notes": notes, "rsi": rsi}


def smart_money_agent(candles: list[dict[str, float]]) -> dict:
    fvg = detect_fvg(candles)
    if not fvg["detected"]:
        return {"score": 0, "notes": [], "fvg": fvg}
    score = 40 if fvg["direction"] == "BULLISH" else -40
    return {"score": score, "notes": [f"{fvg['direction']} Fair Value Gap"], "fvg": fvg}


def derivatives_agent(pcr: float | None) -> dict:
    score = 0; notes = []
    if pcr is None:
        return {"score": 0, "notes": notes}
    if pcr > 1.2:
        score += 30; notes.append(f"Put support (PCR {pcr})")
    elif pcr < 0.8:
        score -= 30; notes.append(f"Call resistance (PCR {pcr})")
    return {"score": score, "notes": notes}


def build_trade_idea(symbol: str, candles: list[dict[str, float]], pcr: float | None = None) -> dict | None:
    if len(candles) < 15:
        return None
    atr = calculate_atr(candles)
    if atr is None or atr <= 0:
        return None
    results = [technical_agent(candles), smart_money_agent(candles), derivatives_agent(pcr)]
    total = sum(r["score"] for r in results)
    if abs(total) < 50:
        return None
    entry = candles[-1]["close"]
    risk = 1.5 * atr
    buy = total > 0
    sl = entry - risk if buy else entry + risk
    t1 = entry + 2.5 * risk if buy else entry - 2.5 * risk
    t2 = entry + 4 * risk if buy else entry - 4 * risk
    return {
        "symbol": symbol, "timeframe": "15m", "trade_type": "BUY" if buy else "SELL",
        "setup_name": "ICT + F&O Confluence Strategy", "entry_price": round(entry, 2),
        "stop_loss": round(sl, 2), "target_1": round(t1, 2), "target_2": round(t2, 2),
        "rr_ratio": 2.5, "confidence_score": min(100.0, abs(total)),
        "rationale": " | ".join(n for r in results for n in r["notes"]),
        "indicators": {"atr": atr, "rsi": results[0]["rsi"], "fvg": results[1]["fvg"], "pcr": pcr},
    }
