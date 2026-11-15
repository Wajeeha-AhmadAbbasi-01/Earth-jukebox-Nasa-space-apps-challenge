"""Dataset-agnostic feature-event timeline composition."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

from .mapping import MappingContract, MappingContractError, normalize_values
from .timeline import TimelineSnapshot

MAX_EVENTS = 100_000


class FeatureEventContractError(ValueError):
    """Raised when feature events cannot be safely composed."""


@dataclass(frozen=True)
class FeatureEvent:
    timestamp_seconds: float
    source_value: float | None
    mapped_value: float | None
    feature_name: str
    mapping_id: str
    mapping_version: str


@dataclass(frozen=True)
class FeatureEventTimeline:
    schema_version: str
    dataset_id: str
    source_version: str
    processing_version: str
    mapping_id: str
    mapping_version: str
    events: tuple[FeatureEvent, ...]


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FeatureEventContractError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise FeatureEventContractError(f"{field} must be a finite number")
    return result


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FeatureEventContractError(f"{field} must be non-empty text")
    return value.strip()


def _verified_envelope(
    envelope: Mapping[str, Any], mapping: MappingContract
) -> tuple[str, str, str, Sequence[Any]]:
    if envelope.get("schema_version") != "feature-envelope.v1":
        raise FeatureEventContractError("unsupported feature envelope schema")
    dataset_id = _text(envelope.get("dataset_id"), "dataset_id")
    source = envelope.get("source")
    verification = envelope.get("verification")
    processing = envelope.get("processing")
    envelope_mapping = envelope.get("mapping")
    if not isinstance(source, Mapping):
        raise FeatureEventContractError("source provenance is required")
    if not isinstance(verification, Mapping):
        raise FeatureEventContractError("verification metadata is required")
    if not isinstance(processing, Mapping):
        raise FeatureEventContractError("processing metadata is required")
    if not isinstance(envelope_mapping, Mapping):
        raise FeatureEventContractError("mapping provenance is required")
    if verification.get("status") != "verified":
        raise FeatureEventContractError(
            "feature events require verification.status=verified"
        )
    if verification.get("schema_verified") is not True:
        raise FeatureEventContractError("feature schema must be verified")
    if verification.get("record_semantics_verified") is not True:
        raise FeatureEventContractError("feature record semantics must be verified")
    source_version = _text(source.get("source_version"), "source.source_version")
    processing_version = _text(processing.get("version"), "processing.version")
    if envelope_mapping.get("name") != mapping.mapping_id:
        raise FeatureEventContractError("mapping provenance ID does not match contract")
    if envelope_mapping.get("version") != mapping.version:
        raise FeatureEventContractError("mapping provenance version does not match contract")
    features = envelope.get("features")
    if not isinstance(features, list):
        raise FeatureEventContractError("features must be a list")
    return dataset_id, source_version, processing_version, features


def build_feature_event_timeline(
    envelope: Mapping[str, Any],
    mapping: MappingContract,
    timeline: TimelineSnapshot,
    feature_name: str,
    timestamps_seconds: Sequence[Any],
) -> FeatureEventTimeline:
    """Compose verified feature values with a bounded playback timeline.

    Timestamps are offsets from the timeline origin and must already be in
    non-decreasing order. Rejecting disorder avoids silently changing source
    event ordering.
    """

    dataset_id, source_version, processing_version, features = _verified_envelope(
        envelope, mapping
    )
    if not isinstance(feature_name, str) or not feature_name.strip():
        raise FeatureEventContractError("feature_name must be non-empty text")
    matching = [
        feature
        for feature in features
        if isinstance(feature, Mapping) and feature.get("name") == feature_name
    ]
    if len(matching) != 1:
        raise FeatureEventContractError("feature_name must identify exactly one feature")
    values = matching[0].get("values")
    if not isinstance(values, list):
        raise FeatureEventContractError("feature values must be a list")
    if len(values) != len(timestamps_seconds):
        raise FeatureEventContractError("timestamps and feature values must have equal length")
    if len(values) > MAX_EVENTS:
        raise FeatureEventContractError("event count exceeds the configured limit")
    if mapping.feature_name != feature_name:
        raise FeatureEventContractError("mapping feature_name does not match selected feature")
    try:
        mapped = normalize_values(values, mapping)
    except MappingContractError as error:
        raise FeatureEventContractError(str(error)) from error

    events: list[FeatureEvent] = []
    previous = -math.inf
    for index, timestamp in enumerate(timestamps_seconds):
        current = _finite(timestamp, f"timestamps_seconds[{index}]")
        if current < 0 or current > timeline.duration_seconds:
            raise FeatureEventContractError(
                f"timestamps_seconds[{index}] must be within the timeline duration"
            )
        if current < previous:
            raise FeatureEventContractError("timestamps must be in non-decreasing order")
        previous = current
        source_value = values[index]
        if source_value is not None:
            source_value = _finite(source_value, f"values[{index}]")
        events.append(
            FeatureEvent(
                timestamp_seconds=current,
                source_value=source_value,
                mapped_value=mapped.values[index],
                feature_name=feature_name,
                mapping_id=mapping.mapping_id,
                mapping_version=mapping.version,
            )
        )
    return FeatureEventTimeline(
        schema_version="feature-events.v1",
        dataset_id=dataset_id,
        source_version=source_version,
        processing_version=processing_version,
        mapping_id=mapping.mapping_id,
        mapping_version=mapping.version,
        events=tuple(events),
    )
