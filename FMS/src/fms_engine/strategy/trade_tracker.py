import sqlite3
import time
from typing import List, Optional
from ..config import settings
from ..contracts.setup_models import ActiveTradeDTO, SetupDirection, TradeState
from ..analytics.excursion_engine import get_pip_scale

class TradeTracker:
    """Tracks active and upcoming trades in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or settings.db_path)
        settings.ensure_directories()
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS active_trades (
                    trade_id TEXT PRIMARY KEY,
                    setup_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_time INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    sl_price REAL NOT NULL,
                    tp_price REAL NOT NULL,
                    current_pnl_pips REAL NOT NULL,
                    current_r REAL NOT NULL,
                    max_favorable_pips REAL NOT NULL,
                    max_adverse_pips REAL NOT NULL,
                    bars_elapsed INTEGER NOT NULL,
                    state TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_trade(self, trade: ActiveTradeDTO) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO active_trades (
                    trade_id, setup_id, symbol, direction, entry_time,
                    entry_price, current_price, sl_price, tp_price,
                    current_pnl_pips, current_r, max_favorable_pips,
                    max_adverse_pips, bars_elapsed, state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.trade_id, trade.setup_id, trade.symbol, trade.direction.value,
                trade.entry_time, trade.entry_price, trade.current_price, trade.sl_price,
                trade.tp_price, trade.current_pnl_pips, trade.current_r,
                trade.max_favorable_pips, trade.max_adverse_pips, trade.bars_elapsed,
                trade.state.value
            ))
            conn.commit()

    def get_trades_by_state(self, state: TradeState) -> List[ActiveTradeDTO]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM active_trades WHERE state = ? ORDER BY entry_time DESC", (state.value,))
            rows = cursor.fetchall()
            return [
                ActiveTradeDTO(
                    trade_id=row[0],
                    setup_id=row[1],
                    symbol=row[2],
                    direction=SetupDirection(row[3]),
                    entry_time=row[4],
                    entry_price=row[5],
                    current_price=row[6],
                    sl_price=row[7],
                    tp_price=row[8],
                    current_pnl_pips=row[9],
                    current_r=row[10],
                    max_favorable_pips=row[11],
                    max_adverse_pips=row[12],
                    bars_elapsed=row[13],
                    state=TradeState(row[14]),
                )
                for row in rows
            ]

