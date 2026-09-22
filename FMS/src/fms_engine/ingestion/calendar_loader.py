from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl
from ..config import settings
from ..contracts.event_models import EventFamily

FAMILY_KEYWORDS = {
    EventFamily.INFLATION: ["cpi", "ppi", "pce", "inflation", "price index", "deflator"],
    EventFamily.LABOR: ["nfp", "payrolls", "unemployment", "jobless", "employment", "claims", "wages", "labor", "earnings", "claimant"],
    EventFamily.MONETARY_POLICY: ["rate decision", "interest rate", "fomc", "ecb", "boe", "rba", "boj", "policy", "statement", "minutes", "cash rate", "refinancing rate", "bank rate"],
    EventFamily.GROWTH: ["gdp", "retail sales", "industrial production", "trade balance", "orders", "factory", "current account"],
    EventFamily.SENTIMENT: ["pmi", "sentiment", "confidence", "zew", "ifo", "ism", "surveys", "michigan"],
}

COMMON_CALENDAR_CSV = Path(r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\fyodor_calendar_master_history.csv")

def classify_event_family(event_name: str) -> EventFamily:
    lower = event_name.lower()
    for family, keywords in FAMILY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return family
    return EventFamily.GROWTH

class CalendarLoader:
    """Manages ingestion, family categorization, and caching of MT5 economic calendar."""

    def __init__(self):
        settings.ensure_directories()

    @property
    def cache_path(self) -> Path:
        return settings.cache_dir / "calendar_events.parquet"

    def ingest_from_master_csv(self, csv_path: Optional[Path] = None) -> pl.DataFrame:
        """
        Parses genuine broker MT5 calendar history CSV (Terminal/Common/Files)
        and converts it to compressed Parquet storage.
        """
        source_path = csv_path or COMMON_CALENDAR_CSV
        if not source_path.exists():
            raise FileNotFoundError(
                f"Historical MT5 calendar master CSV not found at: {source_path}. "
                "Please run FyodorMasterExport script in MT5 to generate it."
            )

        rows: List[Dict[str, Any]] = []
        with open(source_path, "r", encoding="latin-1") as f:
            header_line = f.readline()
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 11:
                    continue

                event_id = str(parts[0])
                value_id = str(parts[1])
                try:
                    ts = int(parts[2])
                except ValueError:
                    continue

                cur = str(parts[3]).upper()
                country = str(parts[4]).upper()
                event_name = ",".join(parts[5:-5]).strip()
                imp = str(parts[-5]).lower()

                # Robust float conversion handling blanks and nulls
                raw_act = parts[-4].strip()
                raw_fct = parts[-3].strip()
                raw_prv = parts[-2].strip()

                try:
                    act = float(raw_act) if raw_act else None
                except ValueError:
                    act = None

                try:
                    fct = float(raw_fct) if raw_fct else None
                except ValueError:
                    fct = None

                try:
                    prv = float(raw_prv) if raw_prv else None
                except ValueError:
                    prv = None

                family = classify_event_family(event_name)

                rows.append({
                    "event_id": event_id,
                    "value_id": value_id,
                    "timestamp": ts,
                    "currency": cur,
                    "country_code": country,
                    "event_name": event_name,
                    "family": family.value,
                    "importance": imp,
                    "actual": act,
                    "forecast": fct,
                    "previous": prv,
                })

        if not rows:
            raise ValueError(f"No valid calendar records could be parsed from {source_path}")

        df = pl.DataFrame(rows).sort("timestamp")
        df.write_parquet(self.cache_path)
        return df

    def load_cached_calendar(self) -> pl.DataFrame:
        """
        Loads cached calendar events from parquet.
        If parquet cache is missing, auto-ingests from verified MT5 common files CSV.
        """
        if self.cache_path.exists():
            try:
                df = pl.read_parquet(self.cache_path).sort("timestamp")
                if not df.is_empty():
                    return df
            except Exception:
                pass

        if COMMON_CALENDAR_CSV.exists():
            return self.ingest_from_master_csv(COMMON_CALENDAR_CSV)

        raise FileNotFoundError(
            "Calendar data is missing on disk. Neither parquet cache nor "
            f"master CSV ({COMMON_CALENDAR_CSV}) was found. "
            "Under the Data Integrity Covenant, synthetic fallback is forbidden."
        )
