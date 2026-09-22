from typing import Any, Dict, List, Optional
import httpx
from ..config import settings

class BridgeClient:
    """HTTP client for reading data from the local MT5 Bridge."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.bridge_url).rstrip("/")
        self.timeout = 30.0

    async def get_health(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/api/v1/health")
            res.raise_for_status()
            return res.json()

    async def get_market_watch(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/api/v1/market-watch")
            res.raise_for_status()
            data = res.json()
            return data.get("symbols", [])

    async def get_ohlc(
        self,
        symbol: str,
        timeframe: str = "H4",
        start_pos: int = 0,
        count: int = 800,
    ) -> Dict[str, Any]:
        params = {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_pos": start_pos,
            "count": count,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/api/v1/ohlc", params=params)
            res.raise_for_status()
            return res.json()

    async def get_calendar(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.get(f"{self.base_url}/api/v1/calendar")
            res.raise_for_status()
            return res.json()

