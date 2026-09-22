from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CalendarEventPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value_id: str = Field(min_length=1, max_length=32)
    event_id: str = Field(min_length=1, max_length=32)
    server_time_seconds: int = Field(ge=0)
    period_seconds: int = Field(ge=0)
    revision: int
    currency: str = Field(min_length=0, max_length=12)
    country_code: str = Field(min_length=0, max_length=12)
    country_name: str = Field(min_length=0, max_length=160)
    name: str = Field(min_length=1, max_length=500)
    event_code: str = Field(min_length=0, max_length=160)
    importance: Literal["none", "low", "medium", "high"]
    unit: int
    multiplier: int
    digits: int = Field(ge=0, le=12)
    time_mode: int
    impact: Literal["none", "positive", "negative"]
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    revised_previous: float | None = None


class CalendarIngestPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    protocol_version: Literal[1]
    kind: Literal["heartbeat", "snapshot", "delta"]
    instance_id: str = Field(min_length=1, max_length=120)
    sent_at_local_seconds: int = Field(ge=0)
    server_time_seconds: int = Field(ge=0)
    gmt_time_seconds: int = Field(ge=0)
    server_utc_offset_seconds: int = Field(ge=-50_400, le=50_400)
    window_from_server_seconds: int | None = Field(default=None, ge=0)
    window_to_server_seconds: int | None = Field(default=None, ge=0)
    previous_request_duration_ms: int = Field(default=0, ge=0, le=120_000)
    change_id: str | None = Field(default=None, max_length=32)
    snapshot_id: str | None = Field(default=None, max_length=120)
    chunk_index: int = Field(default=0, ge=0, le=10_000)
    chunk_count: int = Field(default=1, ge=1, le=10_000)
    events: list[CalendarEventPayload] = Field(default_factory=list, max_length=250)

    @field_validator("snapshot_id")
    @classmethod
    def snapshot_requires_id(cls, value: str | None, info):
        if info.data.get("kind") == "snapshot" and not value:
            raise ValueError("snapshot_id is required for snapshot chunks")
        return value
