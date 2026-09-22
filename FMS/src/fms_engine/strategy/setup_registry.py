import sqlite3
import time
from typing import List, Optional
from ..config import settings
from ..contracts.setup_models import RegisteredSetupDTO, SetupDirection, QuantMethod

class SetupRegistry:
    """Manages persistence and retrieval of codified trading setups in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or settings.db_path)
        settings.ensure_directories()
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS registered_setups (
                    id TEXT PRIMARY KEY,
                    quant_method TEXT NOT NULL DEFAULT 'M-MSD',
                    event_name TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    respect_rate REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    median_mfe_pips REAL NOT NULL,
                    mae_85_pips REAL NOT NULL,
                    recommended_sl_pips REAL NOT NULL,
                    recommended_tp_pips REAL NOT NULL,
                    reward_risk_ratio REAL NOT NULL,
                    trigger_state TEXT NOT NULL,
                    min_z_score REAL NOT NULL,
                    active INTEGER NOT NULL,
                    created_at INTEGER NOT NULL
                )
            """)
            conn.commit()

    def save_setup(self, setup: RegisteredSetupDTO) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO registered_setups (
                    id, quant_method, event_name, currency, symbol, direction, timeframe,
                    respect_rate, sample_count, median_mfe_pips, mae_85_pips,
                    recommended_sl_pips, recommended_tp_pips, reward_risk_ratio,
                    trigger_state, min_z_score, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                setup.id, setup.quant_method.value, setup.event_name, setup.currency, setup.symbol, setup.direction.value,
                setup.timeframe, setup.respect_rate, setup.sample_count, setup.median_mfe_pips,
                setup.mae_85_pips, setup.recommended_sl_pips, setup.recommended_tp_pips,
                setup.reward_risk_ratio, setup.trigger_state, setup.min_z_score,
                1 if setup.active else 0, setup.created_at
            ))
            conn.commit()

    def get_active_setups(self) -> List[RegisteredSetupDTO]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registered_setups WHERE active = 1 ORDER BY respect_rate DESC")
            rows = cursor.fetchall()
            return [
                RegisteredSetupDTO(
                    id=row[0],
                    quant_method=QuantMethod(row[1]) if row[1] in [m.value for m in QuantMethod] else QuantMethod.MSD,
                    event_name=row[2],
                    currency=row[3],
                    symbol=row[4],
                    direction=SetupDirection(row[5]),
                    timeframe=row[6],
                    respect_rate=row[7],
                    sample_count=row[8],
                    median_mfe_pips=row[9],
                    mae_85_pips=row[10],
                    recommended_sl_pips=row[11],
                    recommended_tp_pips=row[12],
                    reward_risk_ratio=row[13],
                    trigger_state=row[14],
                    min_z_score=row[15],
                    active=bool(row[16]),
                    created_at=row[17],
                )
                for row in rows
            ]

    def clear_setups(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM registered_setups")
            conn.commit()

