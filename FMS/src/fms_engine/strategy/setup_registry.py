import sqlite3
import time
from typing import List, Optional
from ..config import settings
from ..contracts.setup_models import RegisteredSetupDTO, SetupDirection

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
                    id, event_name, currency, symbol, direction, timeframe,
                    respect_rate, sample_count, median_mfe_pips, mae_85_pips,
                    recommended_sl_pips, recommended_tp_pips, reward_risk_ratio,
                    trigger_state, min_z_score, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                setup.id, setup.event_name, setup.currency, setup.symbol, setup.direction.value,
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
                    event_name=row[1],
                    currency=row[2],
                    symbol=row[3],
                    direction=SetupDirection(row[4]),
                    timeframe=row[5],
                    respect_rate=row[6],
                    sample_count=row[7],
                    median_mfe_pips=row[8],
                    mae_85_pips=row[9],
                    recommended_sl_pips=row[10],
                    recommended_tp_pips=row[11],
                    reward_risk_ratio=row[12],
                    trigger_state=row[13],
                    min_z_score=row[14],
                    active=bool(row[15]),
                    created_at=row[16],
                )
                for row in rows
            ]
