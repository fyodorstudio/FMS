import sqlite3
from typing import List, Optional
from ..config import settings
from ..contracts.journal_models import JournalCurvePoint, JournalEntryDTO, JournalSummaryDTO
from ..contracts.setup_models import SetupDirection

class JournalLedger:
    """Manages closed trade history and calculates performance R-multiples."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or settings.db_path)
        settings.ensure_directories()
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    trade_id TEXT PRIMARY KEY,
                    setup_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_time INTEGER NOT NULL,
                    exit_time INTEGER NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    pnl_pips REAL NOT NULL,
                    realized_r REAL NOT NULL,
                    exit_reason TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_entry(self, entry: JournalEntryDTO) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO journal_entries (
                    trade_id, setup_id, symbol, event_name, direction,
                    entry_time, exit_time, entry_price, exit_price,
                    pnl_pips, realized_r, exit_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.trade_id, entry.setup_id, entry.symbol, entry.event_name,
                entry.direction.value, entry.entry_time, entry.exit_time,
                entry.entry_price, entry.exit_price, entry.pnl_pips,
                entry.realized_r, entry.exit_reason
            ))
            conn.commit()

    def get_summary(self) -> JournalSummaryDTO:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM journal_entries ORDER BY exit_time ASC")
            rows = cursor.fetchall()

            if not rows:
                return JournalSummaryDTO(
                    total_trades=0,
                    winning_trades=0,
                    losing_trades=0,
                    win_rate=0.0,
                    total_r=0.0,
                    profit_factor=0.0,
                    avg_r_per_trade=0.0,
                    curve=[],
                )

            total_trades = len(rows)
            wins = 0
            losses = 0
            gross_profit_r = 0.0
            gross_loss_r = 0.0
            cumulative_r = 0.0
            curve: List[JournalCurvePoint] = []

            for r in rows:
                realized_r = float(r[10])
                exit_time = int(r[6])
                trade_id = str(r[0])

                if realized_r > 0:
                    wins += 1
                    gross_profit_r += realized_r
                elif realized_r < 0:
                    losses += 1
                    gross_loss_r += abs(realized_r)

                cumulative_r += realized_r
                curve.append(JournalCurvePoint(
                    timestamp=exit_time,
                    cumulative_r=round(cumulative_r, 2),
                    trade_id=trade_id,
                ))

            win_rate = round((wins / total_trades) * 100, 1)
            profit_factor = round(gross_profit_r / gross_loss_r, 2) if gross_loss_r > 0 else (round(gross_profit_r, 2) if gross_profit_r > 0 else 0.0)
            avg_r = round(cumulative_r / total_trades, 2)

            return JournalSummaryDTO(
                total_trades=total_trades,
                winning_trades=wins,
                losing_trades=losses,
                win_rate=win_rate,
                total_r=round(cumulative_r, 2),
                profit_factor=profit_factor,
                avg_r_per_trade=avg_r,
                curve=curve,
            )

