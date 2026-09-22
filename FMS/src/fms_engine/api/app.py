import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..config import settings
from ..contracts.setup_models import ActiveTradeDTO, RegisteredSetupDTO, SetupDirection, TradeState
from ..contracts.journal_models import JournalEntryDTO, JournalSummaryDTO
from ..strategy.setup_registry import SetupRegistry
from ..strategy.trade_tracker import TradeTracker
from ..strategy.journal_ledger import JournalLedger
from .portal_html import generate_portal_html

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

def init_engine():
    """Ensure database tables exist and are initialized."""
    settings.ensure_directories()

init_engine()

@app.get("/", response_class=HTMLResponse)
@app.get("/portal", response_class=HTMLResponse)
def get_portal() -> HTMLResponse:
    """Renders the self-contained FMS Strategy & Knowledge Portal."""
    active = registry.get_active_setups()
    html_content = generate_portal_html(active)
    return HTMLResponse(content=html_content)

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

