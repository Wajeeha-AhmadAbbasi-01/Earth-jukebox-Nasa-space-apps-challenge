"""Dataset-agnostic, deterministic feature mapping declarations."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping


class MappingContractError(ValueError):
    """Raised when a mapping declaration is unsafe or ambiguous."""


@dataclass(frozen=True)
class MappingContract:
    mapping_id: str
    version: str
    feature_name: str
    source_min: float
    source_max: float
    source_unit: str | None
    parameter_name: str
    target_min: float
    target_max: float
    transform: str
    clamp: bool
    missing_value_policy: str


@dataclass(frozen=True)
class NormalizationResult:
    values: tuple[float | None, ...]
    missing_indices: tuple[int, ...]


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MappingContractError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise MappingContractError(f"{field} must be a finite number")
    return result


def _non_empty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MappingContractError(f"{field} must be non-empty text")
    return value.strip()


def parse_mapping_contract(payload: Mapping[str, Any]) -> MappingContract:
    if payload.get("schema_version") != "mapping-contract.v1":
        raise MappingContractError("unsupported mapping contract schema")
    mapping_id = _non_empty_text(payload.get("mapping_id"), "mapping_id")
    version = _non_empty_text(payload.get("version"), "version")
    if not version.startswith("v") or not version[1:].isdigit():
        raise MappingContractError("version must use the vN format")

    input_spec = payload.get("input")
    output_spec = payload.get("output")
    if not isinstance(input_spec, Mapping) or not isinstance(output_spec, Mapping):
        raise MappingContractError("input and output specifications are required")
    feature_name = _non_empty_text(input_spec.get("feature_name"), "input.feature_name")
    parameter_name = _non_empty_text(output_spec.get("parameter_name"), "output.parameter_name")
    source_min = _finite(input_spec.get("source_min"), "input.source_min")
    source_max = _finite(input_spec.get("source_max"), "input.source_max")
    target_min = _finite(output_spec.get("target_min"), "output.target_min")
    target_max = _finite(output_spec.get("target_max"), "output.target_max")
    if source_min >= source_max:
        raise MappingContractError("input source_min must be less than source_max")
    if target_min >= target_max:
        raise MappingContractError("output target_min must be less than target_max")
    source_unit = input_spec.get("unit")
    if source_unit is not None:
        source_unit = _non_empty_text(source_unit, "input.unit")
    transform = payload.get("transform", "linear")
    if transform != "linear":
        raise MappingContractError("only the deterministic linear transform is supported")
    clamp = payload.get("clamp", True)
    if not isinstance(clamp, bool):
        raise MappingContractError("clamp must be boolean")
    missing_value_policy = payload.get("missing_value_policy")
    if missing_value_policy not in {"preserve_missing", "reject_missing"}:
        raise MappingContractError("unsupported missing_value_policy")
    return MappingContract(
        mapping_id=mapping_id,
        version=version,
        feature_name=feature_name,
        source_min=source_min,
        source_max=source_max,
        source_unit=source_unit,
        parameter_name=parameter_name,
        target_min=target_min,
        target_max=target_max,
        transform=transform,
        clamp=clamp,
        missing_value_policy=missing_value_policy,
    )


def normalize_values(
    values: list[Any] | tuple[Any, ...], contract: MappingContract
) -> NormalizationResult:
    """Normalize values without converting missing/invalid values to zero."""

    normalized: list[float | None] = []
    missing: list[int] = []
    source_span = contract.source_max - contract.source_min
    target_span = contract.target_max - contract.target_min
    for index, value in enumerate(values):
        if value is None:
            if contract.missing_value_policy == "reject_missing":
                raise MappingContractError(f"value {index} is missing")
            normalized.append(None)
            missing.append(index)
            continue
        numeric = _finite(value, f"value {index}")
        if contract.clamp:
            numeric = min(max(numeric, contract.source_min), contract.source_max)
        elif not contract.source_min <= numeric <= contract.source_max:
            raise MappingContractError(f"value {index} is outside the declared source range")
        ratio = (numeric - contract.source_min) / source_span
        normalized.append(contract.target_min + ratio * target_span)
    return NormalizationResult(tuple(normalized), tuple(missing))
