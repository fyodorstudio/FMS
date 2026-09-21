from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from threading import RLock
from time import perf_counter
from typing import Literal

ActivitySeverity = Literal["info", "success", "warning", "error"]


def utc_milliseconds() -> int:
    return int(datetime.now(UTC).timestamp() * 1000)


@dataclass(frozen=True)
class ActivityEvent:
    sequence: int
    occurred_at: int
    source: str
    severity: ActivitySeverity
    action: str
    detail: str | None = None


class ActivityLedger:
    def __init__(self, capacity: int = 500) -> None:
        self._events: deque[ActivityEvent] = deque(maxlen=capacity)
        self._sequence = 0
        self._lock = RLock()
        self._last_signature: tuple[str, str, str | None] | None = None
        self._last_signature_at = 0

    def append(
        self,
        source: str,
        action: str,
        detail: str | None = None,
        severity: ActivitySeverity = "info",
    ) -> None:
        now = utc_milliseconds()
        signature = (source, action, detail)
        with self._lock:
            if signature == self._last_signature and now - self._last_signature_at < 500:
                return
            self._sequence += 1
            self._events.append(
                ActivityEvent(self._sequence, now, source, severity, action, detail),
            )
            self._last_signature = signature
            self._last_signature_at = now

    def after(self, sequence: int) -> dict[str, object]:
        with self._lock:
            events = [asdict(event) for event in self._events if event.sequence > sequence]
            latest = self._sequence
        return {"events": events, "latest_sequence": latest}


@dataclass
class OperationTelemetry:
    state: Literal["idle", "running", "failed"] = "idle"
    operation: str | None = None
    operation_started_at: int | None = None
    last_success_at: int | None = None
    last_duration_ms: int | None = None
    last_error: str | None = None
    count: int | None = None


class HeartbeatRegistry:
    def __init__(self) -> None:
        self._components: dict[str, OperationTelemetry] = {}
        self._started: dict[tuple[str, int], float] = {}
        self._active_tokens: dict[str, int] = {}
        self._token_sequence = 0
        self._lock = RLock()

    def begin(self, component: str, operation: str) -> int:
        now = utc_milliseconds()
        with self._lock:
            self._token_sequence += 1
            token = self._token_sequence
            telemetry = self._components.setdefault(component, OperationTelemetry())
            telemetry.state = "running"
            telemetry.operation = operation
            telemetry.operation_started_at = now
            telemetry.last_error = None
            self._active_tokens[component] = token
            self._started[(component, token)] = perf_counter()
            return token

    def succeed(self, component: str, token: int, count: int | None = None) -> int:
        with self._lock:
            telemetry = self._components.setdefault(component, OperationTelemetry())
            started = self._started.pop((component, token), perf_counter())
            duration = max(0, round((perf_counter() - started) * 1000))
            if self._active_tokens.get(component) != token:
                return duration
            telemetry.state = "idle"
            telemetry.operation_started_at = None
            telemetry.last_success_at = utc_milliseconds()
            telemetry.last_duration_ms = duration
            telemetry.last_error = None
            telemetry.count = count
            return duration

    def fail(self, component: str, token: int, message: str) -> int:
        with self._lock:
            telemetry = self._components.setdefault(component, OperationTelemetry())
            started = self._started.pop((component, token), perf_counter())
            duration = max(0, round((perf_counter() - started) * 1000))
            if self._active_tokens.get(component) != token:
                return duration
            telemetry.state = "failed"
            telemetry.operation_started_at = None
            telemetry.last_duration_ms = duration
            telemetry.last_error = message
            return duration

    def snapshot(self) -> dict[str, dict[str, object]]:
        with self._lock:
            return {
                name: asdict(telemetry)
                for name, telemetry in self._components.items()
            }
