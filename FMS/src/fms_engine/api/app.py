import time
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..config import settings
from ..contracts.setup_models import ActiveTradeDTO, RegisteredSetupDTO, SetupDirection, TradeState, QuantMethod
from ..contracts.journal_models import JournalEntryDTO, JournalSummaryDTO
from ..contracts.library_models import MethodSectionContract, LibrarySummaryContract, AccordionState
from ..strategy.setup_registry import SetupRegistry
from ..strategy.trade_tracker import TradeTracker
from ..strategy.journal_ledger import JournalLedger
from ..ingestion.candle_loader import CandleLoader
from ..ingestion.calendar_loader import CalendarLoader
from ..analytics.macro_divergence_engine import MacroDivergenceEngine
from ..analytics.policy_spread_engine import PolicySpreadEngine
from ..analytics.terms_of_trade_engine import TermsOfTradeEngine
from ..analytics.carry_unwind_engine import CarryUnwindEngine
from ..analytics.liquidity_absorption_engine import LiquidityAbsorptionEngine
from ..analytics.signal_evaluator import SignalEvaluator
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
candle_loader = CandleLoader()
calendar_loader = CalendarLoader()
signal_evaluator = SignalEvaluator(horizon_bars=24)

tot_engine = TermsOfTradeEngine(min_pulse_threshold=1.00)
carry_engine = CarryUnwindEngine(min_vol_z=1.50)
lar_engine = LiquidityAbsorptionEngine(min_expansion_ratio=1.50, min_wick_ratio=0.40)

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
        "registered_setups": len(registry.get_active_setups()),
        "timestamp": int(time.time()),
    }

@app.get("/api/fms/setups")
def get_setups() -> Dict[str, Any]:
    active = registry.get_active_setups()
    return {
        "setups": [s.model_dump() for s in active],
        "count": len(active),
    }

@app.get("/api/fms/summary")
def get_summary() -> Dict[str, Any]:
    """Returns method-by-method aggregate metrics across the 5 quantitative factor models."""
    active = registry.get_active_setups()
    method_meta = {
        QuantMethod.MSD: {
            "name": "Macro Surprise Divergence",
            "code": "M-MSD",
            "desc": "Standardized release surprise vector divergence with 2D S&R zones.",
        },
        QuantMethod.PYS: {
            "name": "Policy & Real Yield Spread Momentum",
            "code": "M-PYS",
            "desc": "Irving Fisher real rate differentials and sovereign capital gravity.",
        },
        QuantMethod.TOT: {
            "name": "Terms-of-Trade Commodity Pulse",
            "code": "M-TOT",
            "desc": "Commodity export shocks vs. structural resource net importers.",
        },
        QuantMethod.VRC: {
            "name": "Volatility Regime & Carry Unwind",
            "code": "M-VRC",
            "desc": "Systemic liquidation cascades and mandatory institutional VaR de-grossing.",
        },
        QuantMethod.LAR: {
            "name": "Liquidity Absorption Rejection",
            "code": "M-LAR",
            "desc": "Sovereign defense footprints: 1.5x+ ATR expansion with 40%+ rejection wicks.",
        },
    }

    methods_out = []
    total_net_r = 0.0
    for qm in QuantMethod:
        setups_m = [s for s in active if s.quant_method == qm]
        meta = method_meta.get(qm, {"name": qm.value, "code": qm.value, "desc": "", "net_r": 0.0})
        count = len(setups_m)
        avg_win_rate = (sum(s.respect_rate for s in setups_m) / count) if count > 0 else 0.0
        avg_rr = (sum(s.reward_risk_ratio for s in setups_m) / count) if count > 0 else 1.0
        # Calculate real aggregate Net R from empirical setup observations:
        net_r = sum(
            (s.sample_count * s.respect_rate * s.reward_risk_ratio - s.sample_count * (1.0 - s.respect_rate))
            for s in setups_m
        ) if count > 0 else 0.0
        net_r = round(net_r, 1)
        total_net_r += net_r

        methods_out.append({
            "method_id": qm.name,
            "code": meta["code"],
            "name": meta["name"],
            "description": meta["desc"],
            "setup_count": count,
            "average_win_rate": round(avg_win_rate, 3),
            "average_reward_risk": round(avg_rr, 2),
            "aggregate_net_r": net_r,
        })

    return {
        "methods": methods_out,
        "total_setups": len(active),
        "total_net_r": round(total_net_r, 1),
        "active_methods_count": len([m for m in methods_out if m["setup_count"] > 0]),
        "timestamp": int(time.time()),
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
def get_signals(symbol: str = Query(default="EURUSD"), limit: int = Query(default=35)) -> Dict[str, Any]:
    """Returns verified empirical signals and path-evaluated outcome markers for the chart overlay."""
    candles_df = candle_loader.load_cached_candles(symbol.upper(), "H1")
    if candles_df is None or len(candles_df) < 50:
        return {"symbol": symbol.upper(), "signals": []}

    try:
        cal_df = calendar_loader.load_cached_calendar()
    except Exception:
        cal_df = None

    signals = signal_evaluator.generate_all_signals(
        symbol=symbol.upper(),
        calendar_df=cal_df,
        candles_df=candles_df,
        limit=limit,
    )

    return {
        "symbol": symbol.upper(),
        "signals": signals,
    }

