import csv
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import polars as pl
from ..config import settings

def sync_mt5_candles(
    symbols: Optional[List[str]] = None,
    timeframe: str = "H4",
    count: int = 5000,
) -> Dict[str, int]:
    """
    Syncs candles from MT5 via the bridge Python environment and writes Parquet caches.
    This enables offline research with true institutional tick data without modifying the bridge.
    """
    settings.ensure_directories()
    symbols = symbols or settings.major_forex_extended
    bridge_py = settings.root_dir.parent / "bridge" / ".venv" / "Scripts" / "python.exe"

    if not bridge_py.exists():
        raise FileNotFoundError(f"Bridge Python environment not found at: {bridge_py}")

    results: Dict[str, int] = {}
    temp_csv_dir = settings.cache_dir / "_temp_sync"
    temp_csv_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Script run inside bridge Python environment where MetaTrader5 is installed
        extraction_script = f"""
import MetaTrader5 as mt5
import csv
from pathlib import Path

if not mt5.initialize():
    print("MT5_INIT_FAILED")
    exit(1)

tf_map = {{
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}}
tf = tf_map.get("{timeframe}", mt5.TIMEFRAME_H4)
out_dir = Path(r"{temp_csv_dir}")

symbols = {symbols}
for sym in symbols:
    rates = mt5.copy_rates_from_pos(sym, tf, 0, {count})
    if rates is None or len(rates) == 0:
        continue
    csv_file = out_dir / f"{{sym}}.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"])
        for r in rates:
            writer.writerow([int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), int(r[5]), int(r[6]), int(r[7])])
mt5.shutdown()
print("MT5_SYNC_COMPLETE")
"""
        proc = subprocess.run(
            [str(bridge_py), "-c", extraction_script],
            capture_output=True,
            text=True,
            check=False,
        )

        if "MT5_SYNC_COMPLETE" not in proc.stdout:
            raise RuntimeError(f"MT5 candle sync failed: {proc.stderr or proc.stdout}")

        # Ingest CSVs into Polars and write Parquet
        for sym in symbols:
            csv_path = temp_csv_dir / f"{sym}.csv"
            if not csv_path.exists():
                results[sym] = 0
                continue

            df = pl.read_csv(csv_path)
            if df.is_empty():
                results[sym] = 0
                continue

            parquet_path = settings.cache_dir / f"candles_{sym}_{timeframe}.parquet"
            df.sort("time").write_parquet(parquet_path)
            results[sym] = len(df)

    finally:
        # Cleanup temp CSVs
        for f in temp_csv_dir.glob("*.csv"):
            try:
                f.unlink()
            except OSError:
                pass
        try:
            temp_csv_dir.rmdir()
        except OSError:
            pass

    return results
