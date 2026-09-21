from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass(frozen=True)
class TerminalProcess:
    pid: int
    executable: str


class MultipleTerminalProcessesError(RuntimeError):
    pass


def find_terminal_process(configured_path: str | None) -> TerminalProcess | None:
    configured = str(Path(configured_path).resolve()).casefold() if configured_path else None
    candidates: list[tuple[float, TerminalProcess]] = []

    for process in psutil.process_iter(("pid", "name", "exe", "create_time")):
        try:
            name = (process.info.get("name") or "").casefold()
            executable = process.info.get("exe") or ""
            if name not in {"terminal.exe", "terminal64.exe"}:
                continue
            resolved = str(Path(executable).resolve()) if executable else ""
            if configured and resolved.casefold() != configured:
                continue
            candidates.append(
                (
                    float(process.info.get("create_time") or 0),
                    TerminalProcess(int(process.info["pid"]), resolved),
                ),
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            continue

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    distinct_paths = sorted({candidate.executable for _, candidate in candidates})
    if configured is None and len(distinct_paths) > 1:
        raise MultipleTerminalProcessesError(
            "Multiple MT5 installations are running; set FYODOR_MT5_TERMINAL_PATH to the intended terminal64.exe",
        )
    return candidates[0][1]
