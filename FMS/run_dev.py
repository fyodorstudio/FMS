from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    fms_directory = Path(__file__).resolve().parent
    source_directory = fms_directory / "src"
    sys.path.insert(0, str(source_directory))

    try:
        import uvicorn
    except ModuleNotFoundError:
        print(
            "FMS dependencies are missing. Run: "
            "python -m pip install -e ./fms",
            file=sys.stderr,
        )
        return 1

    uvicorn.run(
        "fms_engine.api.app:app",
        host="127.0.0.1",
        port=8002,
        log_level="info",
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
