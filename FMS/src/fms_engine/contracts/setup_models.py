from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class SetupDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class QuantMethod(str, Enum):
    MSD = "M-MSD"  # Macro Surprise Divergence
    PYS = "M-PYS"  # Policy & Real Yield Spread
    TOT = "M-TOT"  # Terms-of-Trade Commodity Pulse
    VRC = "M-VRC"  # Volatility Regime & Carry Unwind
    LAR = "M-LAR"  # Liquidity Absorption Rejection

class RegisteredSetupDTO(BaseModel):
    id: str
    quant_method: QuantMethod = QuantMethod.MSD
    event_name: str
    currency: str
    symbol: str
    direction: SetupDirection
    timeframe: str = "H4"
    respect_rate: float
    sample_count: int
    median_mfe_pips: float
    mae_85_pips: float
    recommended_sl_pips: float
    recommended_tp_pips: float
    reward_risk_ratio: float
    trigger_state: str  # e.g., "full_acceleration"
    min_z_score: float = 0.50
    active: bool = True
    created_at: int

class TradeState(str, Enum):
    UPCOMING = "upcoming"
    ACTIVE = "active"
    CLOSED = "closed"

class ActiveTradeDTO(BaseModel):
    trade_id: str
    setup_id: str
    symbol: str
    direction: SetupDirection
    entry_time: int
    entry_price: float
    current_price: float
    sl_price: float
    tp_price: float
    current_pnl_pips: float
    current_r: float
    max_favorable_pips: float = 0.0
    max_adverse_pips: float = 0.0
    bars_elapsed: int = 0
    state: TradeState = TradeState.ACTIVE

