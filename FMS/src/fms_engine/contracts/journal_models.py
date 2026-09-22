from typing import List, Optional
from pydantic import BaseModel
from .setup_models import SetupDirection

class JournalEntryDTO(BaseModel):
    trade_id: str
    setup_id: str
    symbol: str
    event_name: str
    direction: SetupDirection
    entry_time: int
    exit_time: int
    entry_price: float
    exit_price: float
    pnl_pips: float
    realized_r: float
    exit_reason: str  # "take_profit", "stop_loss", "macro_supercedence", "time_decay", "bar_expiry"

class JournalCurvePoint(BaseModel):
    timestamp: int
    cumulative_r: float
    trade_id: str

class JournalSummaryDTO(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_r: float
    profit_factor: float
    avg_r_per_trade: float
    curve: List[JournalCurvePoint] = []

