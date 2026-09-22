import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..config import settings
from ..contracts.setup_models import ActiveTradeDTO, RegisteredSetupDTO, SetupDirection, TradeState
from ..contracts.journal_models import JournalEntryDTO, JournalSummaryDTO
from ..strategy.setup_registry import SetupRegistry
from ..strategy.trade_tracker import TradeTracker
from ..strategy.journal_ledger import JournalLedger

app = FastAPI(
    title="Fyodor Macro Signal (FMS) Engine API",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

registry = SetupRegistry()
tracker = TradeTracker()
journal = JournalLedger()

def seed_sample_data_if_empty():
    """Seeds baseline registered setups and initial journal history if empty."""
    setups = registry.get_active_setups()
    if not setups:
        now = int(time.time())
        sample_setups = [
            RegisteredSetupDTO(
                id="setup-nfp-eurusd",
                event_name="US Non-Farm Payrolls",
                currency="USD",
                symbol="EURUSD",
                direction=SetupDirection.SELL,
                timeframe="H4",
                respect_rate=0.78,
                sample_count=24,
                median_mfe_pips=52.4,
                mae_85_pips=18.6,
                recommended_sl_pips=22.0,
                recommended_tp_pips=50.0,
                reward_risk_ratio=2.27,
                trigger_state="full_acceleration",
                min_z_score=0.60,
                active=True,
                created_at=now - 86400 * 30,
            ),
            RegisteredSetupDTO(
                id="setup-cpi-usdjpy",
                event_name="US Core CPI (MoM)",
                currency="USD",
                symbol="USDJPY",
                direction=SetupDirection.BUY,
                timeframe="H4",
                respect_rate=0.72,
                sample_count=20,
                median_mfe_pips=68.0,
                mae_85_pips=24.5,
                recommended_sl_pips=28.0,
                recommended_tp_pips=65.0,
                reward_risk_ratio=2.32,
                trigger_state="full_acceleration",
                min_z_score=0.50,
                active=True,
                created_at=now - 86400 * 20,
            ),
            RegisteredSetupDTO(
                id="setup-ecb-eurusd",
                event_name="ECB Interest Rate Decision",
                currency="EUR",
                symbol="EURUSD",
                direction=SetupDirection.BUY,
                timeframe="H4",
                respect_rate=0.69,
                sample_count=16,
                median_mfe_pips=48.2,
                mae_85_pips=21.0,
                recommended_sl_pips=25.0,
                recommended_tp_pips=45.0,
                reward_risk_ratio=1.80,
                trigger_state="full_acceleration",
                min_z_score=0.50,
                active=True,
                created_at=now - 86400 * 15,
            ),
        ]
        for s in sample_setups:
            registry.save_setup(s)

        # Seed sample active trade
        tracker.save_trade(ActiveTradeDTO(
            trade_id="trade-active-001",
            setup_id="setup-nfp-eurusd",
            symbol="EURUSD",
            direction=SetupDirection.SELL,
            entry_time=now - 3600 * 12,
            entry_price=1.0850,
            current_price=1.0818,
            sl_price=1.0872,
            tp_price=1.0800,
            current_pnl_pips=32.0,
            current_r=1.45,
            max_favorable_pips=36.5,
            max_adverse_pips=8.2,
            bars_elapsed=3,
            state=TradeState.ACTIVE,
        ))

        # Seed sample journal closed trades
        sample_journal = [
            JournalEntryDTO(
                trade_id="trade-closed-001",
                setup_id="setup-nfp-eurusd",
                symbol="EURUSD",
                event_name="US Non-Farm Payrolls",
                direction=SetupDirection.SELL,
                entry_time=now - 86400 * 28,
                exit_time=now - 86400 * 25,
                entry_price=1.0920,
                exit_price=1.0870,
                pnl_pips=50.0,
                realized_r=2.27,
                exit_reason="take_profit",
            ),
            JournalEntryDTO(
                trade_id="trade-closed-002",
                setup_id="setup-cpi-usdjpy",
                symbol="USDJPY",
                event_name="US Core CPI (MoM)",
                direction=SetupDirection.BUY,
                entry_time=now - 86400 * 18,
                exit_time=now - 86400 * 15,
                entry_price=154.20,
                exit_price=153.92,
                pnl_pips=-28.0,
                realized_r=-1.00,
                exit_reason="stop_loss",
            ),
            JournalEntryDTO(
                trade_id="trade-closed-003",
                setup_id="setup-ecb-eurusd",
                symbol="EURUSD",
                event_name="ECB Interest Rate Decision",
                direction=SetupDirection.BUY,
                entry_time=now - 86400 * 12,
                exit_time=now - 86400 * 9,
                entry_price=1.0780,
                exit_price=1.0825,
                pnl_pips=45.0,
                realized_r=1.80,
                exit_reason="take_profit",
            ),
        ]
        for entry in sample_journal:
            journal.add_entry(entry)

seed_sample_data_if_empty()

@app.get("/api/fms/health")
def get_health() -> Dict[str, Any]:
    return {
        "status": "operational",
        "engine": "Fyodor Macro Signal (FMS)",
        "version": "0.1.0",
        "timestamp": int(time.time()),
    }

@app.get("/api/fms/setups")
def get_setups() -> Dict[str, Any]:
    active = registry.get_active_setups()
    return {
        "setups": [s.model_dump() for s in active],
        "count": len(active),
    }

@app.get("/api/fms/trades")
def get_trades(state: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    if state:
        trades = tracker.get_trades_by_state(TradeState(state))
    else:
        active = tracker.get_trades_by_state(TradeState.ACTIVE)
        upcoming = tracker.get_trades_by_state(TradeState.UPCOMING)
        closed = tracker.get_trades_by_state(TradeState.CLOSED)
        trades = active + upcoming + closed

    return {
        "trades": [t.model_dump() for t in trades],
        "count": len(trades),
    }

@app.get("/api/fms/journal")
def get_journal() -> Dict[str, Any]:
    summary = journal.get_summary()
    return summary.model_dump()

@app.get("/api/fms/signals")
def get_signals(symbol: str = Query(default="EURUSD")) -> Dict[str, Any]:
    """Returns historical signals and outcome markers for the chart overlay."""
    now = int(time.time())
    signals = [
        {
            "id": "sig-001",
            "time": now - 86400 * 28,
            "direction": "SELL",
            "event_name": "US Non-Farm Payrolls",
            "entry_price": 1.0920,
            "target_price": 1.0870,
            "stop_price": 1.0942,
            "outcome": "win",
            "pnl_pips": 50.0,
            "realized_r": 2.27,
        },
        {
            "id": "sig-002",
            "time": now - 86400 * 12,
            "direction": "BUY",
            "event_name": "ECB Interest Rate Decision",
            "entry_price": 1.0780,
            "target_price": 1.0825,
            "stop_price": 1.0755,
            "outcome": "win",
            "pnl_pips": 45.0,
            "realized_r": 1.80,
        },
    ]
    return {
        "symbol": symbol,
        "signals": signals,
    }
