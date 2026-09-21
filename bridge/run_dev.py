from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    bridge_directory = Path(__file__).resolve().parent
    source_directory = bridge_directory / "src"
    sys.path.insert(0, str(source_directory))

    try:
        import uvicorn
    except ModuleNotFoundError:
        print(
            "Bridge dependencies are missing. Run: "
            "python -m pip install -e ./bridge",
            file=sys.stderr,
        )
        return 1

    uvicorn.run(
        "fyodor_bridge.app:app",
        host="127.0.0.1",
        port=8001,
        log_level="info",
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
