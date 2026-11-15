"""Fail-closed contract for verified ISS LIS lightning records.

The SVS audit verifies that records contain latitude, longitude, and detection
time, but does not verify the archive schema, record kind, units, or quality
flags. This module therefore refuses to parse a payload unless an upstream
adapter explicitly proves that its source schema was verified.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any, Mapping

MAX_RECORDS = 100_000
REQUIRED_FIELDS = frozenset({"latitude", "longitude", "detection_time"})


class LightningContractError(ValueError):
    """Raised when source metadata or a record cannot be trusted."""


@dataclass(frozen=True)
class LightningRecord:
    latitude: float
    longitude: float
    detection_time: datetime
    source_record_type: str
    source_schema_id: str


@dataclass(frozen=True)
class VerifiedLightningPayload:
    source_schema_id: str
    source_record_type: str
    records: tuple[LightningRecord, ...]


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LightningContractError(f"{field} must be a finite number")
    result = float(value)
    if result != result or result in (float("inf"), float("-inf")):
        raise LightningContractError(f"{field} must be a finite number")
    return result


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise LightningContractError("detection_time must be a non-empty ISO-8601 string")
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise LightningContractError("detection_time must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise LightningContractError("detection_time must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_verified_payload(payload: Mapping[str, Any]) -> VerifiedLightningPayload:
    """Parse only a payload backed by explicitly verified source metadata."""

    if payload.get("source_schema_verified") is not True:
        raise LightningContractError(
            "refusing lightning records: source schema is not explicitly verified"
        )
    schema_id = payload.get("source_schema_id")
    record_type = payload.get("source_record_type")
    if not isinstance(schema_id, str) or not schema_id.strip():
        raise LightningContractError("source_schema_id is required")
    if not isinstance(record_type, str) or not record_type.strip():
        raise LightningContractError("source_record_type is required and cannot be inferred")
    records = payload.get("records")
    if not isinstance(records, list):
        raise LightningContractError("records must be a list")
    if len(records) > MAX_RECORDS:
        raise LightningContractError("record count exceeds the configured limit")

    parsed: list[LightningRecord] = []
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise LightningContractError(f"record {index} must be an object")
        missing = REQUIRED_FIELDS.difference(record)
        if missing:
            raise LightningContractError(
                f"record {index} is missing required fields: {', '.join(sorted(missing))}"
            )
        latitude = _finite_number(record["latitude"], "latitude")
        longitude = _finite_number(record["longitude"], "longitude")
        if not -90 <= latitude <= 90:
            raise LightningContractError(f"record {index} latitude is outside [-90, 90]")
        if not -180 <= longitude <= 180:
            raise LightningContractError(f"record {index} longitude is outside [-180, 180]")
        parsed.append(
            LightningRecord(
                latitude=latitude,
                longitude=longitude,
                detection_time=_timestamp(record["detection_time"]),
                source_record_type=record_type,
                source_schema_id=schema_id,
            )
        )
    return VerifiedLightningPayload(
        source_schema_id=schema_id,
        source_record_type=record_type,
        records=tuple(parsed),
    )


def parse_verified_json(text: str) -> VerifiedLightningPayload:
    """Parse bounded JSON text; network access and URL resolution are excluded."""

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        raise LightningContractError("payload is not valid JSON") from error
    if not isinstance(payload, Mapping):
        raise LightningContractError("payload root must be an object")
    return parse_verified_payload(payload)
