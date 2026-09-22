from pathlib import Path
from pydantic import BaseModel

class FmsConfig(BaseModel):
    bridge_url: str = "http://127.0.0.1:8001"
    api_host: str = "127.0.0.1"
    api_port: int = 8002

    # Storage paths
    root_dir: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = Path(__file__).resolve().parents[2] / "data"
    cache_dir: Path = Path(__file__).resolve().parents[2] / "data" / "cache"
    db_path: Path = Path(__file__).resolve().parents[2] / "data" / "fms_store.db"

    # Quant parameters
    max_h4_bars: int = 60
    min_reward_risk_ratio: float = 1.30
    min_respect_rate: float = 0.65
    mae_percentile: float = 0.85
    mfe_percentile: float = 0.50
    sl_atr_buffer: float = 0.20

    major_forex_extended: list[str] = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
        "EURJPY", "GBPJPY", "EURGBP", "AUDJPY", "EURCAD"
    ]
    g8_currencies: list[str] = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

settings = FmsConfig()
