from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

@dataclass
class TradeIdea:
    symbol: str
    timeframe: str
    trade_type: str
    setup_name: str
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    rr_ratio: float
    confidence_score: float
    rationale: str
    timestamp: str
    status: str = "OPEN"
    realized_pnl: Optional[float] = None

    def to_dict(self):
        return asdict(self)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
