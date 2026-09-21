from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Literal

from .runtime_activity import ActivityLedger, utc_milliseconds


@dataclass
class SnapshotStage:
    chunk_count: int
    chunks: dict[int, list[dict[str, Any]]]
    instance_id: str
    server_utc_offset_seconds: int


class CalendarStore:
    def __init__(self, activity: ActivityLedger) -> None:
        self._activity = activity
        self._lock = RLock()
        self._events: dict[str, dict[str, Any]] = {}
        self._stages: dict[str, SnapshotStage] = {}
        self._instance_id: str | None = None
        self._last_heartbeat_at: int | None = None
        self._last_snapshot_at: int | None = None
        self._last_update_at: int | None = None
        self._server_time_seconds: int | None = None
        self._server_utc_offset_seconds: int | None = None
        self._change_id: str | None = None
        self._publisher_request_duration_ms: int | None = None
        self._clock_trust: Literal["unavailable", "observed"] = "unavailable"

    def ingest(self, payload: dict[str, Any]) -> dict[str, object]:
        kind = payload["kind"]
        instance_id = payload["instance_id"]
        now = utc_milliseconds()

        with self._lock:
            if self._instance_id != instance_id:
                previous = self._instance_id
                self._instance_id = instance_id
                self._events.clear()
                self._stages.clear()
                self._last_snapshot_at = None
                self._last_update_at = None
                if previous is not None:
                    self._activity.append("Calendar", "Publisher generation changed", instance_id, "warning")

            self._last_heartbeat_at = now
            self._server_time_seconds = int(payload["server_time_seconds"])
            self._server_utc_offset_seconds = int(payload["server_utc_offset_seconds"])
            self._change_id = payload.get("change_id")
            self._publisher_request_duration_ms = int(payload.get("previous_request_duration_ms", 0))
            self._clock_trust = "observed"

            if kind == "snapshot":
                committed = self._ingest_snapshot_chunk(payload, now)
            elif kind == "delta":
                for event in payload.get("events", []):
                    self._events[event["value_id"]] = event
                self._last_update_at = now
                committed = True
            else:
                committed = True

            return {
                "accepted": True,
                "committed": committed,
                "event_count": len(self._events),
                "received_at": now,
            }

    def _ingest_snapshot_chunk(self, payload: dict[str, Any], now: int) -> bool:
        snapshot_id = payload["snapshot_id"]
        chunk_index = int(payload["chunk_index"])
        chunk_count = int(payload["chunk_count"])
        stage = self._stages.get(snapshot_id)
        if stage is None:
            stage = SnapshotStage(
                chunk_count=chunk_count,
                chunks={},
                instance_id=payload["instance_id"],
                server_utc_offset_seconds=int(payload["server_utc_offset_seconds"]),
            )
            self._stages = {snapshot_id: stage}
        if stage.chunk_count != chunk_count:
            raise ValueError("Snapshot chunk count changed during transfer")
        stage.chunks[chunk_index] = payload.get("events", [])
        if len(stage.chunks) != chunk_count:
            return False

        next_events: dict[str, dict[str, Any]] = {}
        for index in range(chunk_count):
            if index not in stage.chunks:
                return False
            for event in stage.chunks[index]:
                next_events[event["value_id"]] = event
        self._events = next_events
        self._last_snapshot_at = now
        self._last_update_at = now
        self._stages.clear()
        self._activity.append(
            "Calendar",
            "Snapshot committed",
            f"{len(next_events)} events · atomic {chunk_count} chunk transfer",
            "success",
        )
        return True

    def health(self) -> dict[str, object]:
        with self._lock:
            age = utc_milliseconds() - self._last_heartbeat_at if self._last_heartbeat_at else None
            if self._last_heartbeat_at is None:
                status = "waiting-for-publisher"
            elif age is not None and age > 30_000:
                status = "stale"
            elif self._last_snapshot_at is None:
                status = "awaiting-snapshot"
            else:
                status = "live"
            return {
                "status": status,
                "instance_id": self._instance_id,
                "last_heartbeat_at": self._last_heartbeat_at,
                "last_snapshot_at": self._last_snapshot_at,
                "last_update_at": self._last_update_at,
                "server_time_seconds": self._server_time_seconds,
                "server_utc_offset_seconds": self._server_utc_offset_seconds,
                "change_id": self._change_id,
                "publisher_request_duration_ms": self._publisher_request_duration_ms,
                "clock_trust": self._clock_trust,
                "event_count": len(self._events),
            }

    def events(self) -> dict[str, object]:
        with self._lock:
            offset = self._server_utc_offset_seconds
            events: list[dict[str, Any]] = []
            for stored in self._events.values():
                event = dict(stored)
                server_seconds = int(event["server_time_seconds"])
                event["release_at"] = (server_seconds - offset) * 1000 if offset is not None else None
                events.append(event)
            events.sort(key=lambda event: (event["server_time_seconds"], event["value_id"]))
            return {
                "events": events,
                "source": self.health(),
                "observed_at": utc_milliseconds(),
            }
