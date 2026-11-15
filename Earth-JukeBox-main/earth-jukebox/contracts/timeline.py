"""Pure shared playback timeline state; no browser, media, or audio dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Any, Mapping

MAX_DURATION_SECONDS = 86_400.0
MIN_SPEED = 0.125
MAX_SPEED = 8.0
EPSILON = 1e-9


class TimelineContractError(ValueError):
    """Raised when timeline input or an operation violates the contract."""


class PlaybackState(str, Enum):
    STOPPED = "stopped"
    PAUSED = "paused"
    PLAYING = "playing"


@dataclass(frozen=True)
class TimelineSnapshot:
    duration_seconds: float
    position_seconds: float
    speed: float
    state: PlaybackState


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TimelineContractError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise TimelineContractError(f"{field} must be a finite number")
    return result


def _bounded_position(value: Any, duration: float) -> float:
    position = _finite(value, "position_seconds")
    if position < 0 or position > duration:
        raise TimelineContractError("position_seconds must be within the duration")
    return position


def _bounded_speed(value: Any) -> float:
    speed = _finite(value, "speed")
    if speed < MIN_SPEED or speed > MAX_SPEED:
        raise TimelineContractError(
            f"speed must be between {MIN_SPEED} and {MAX_SPEED}"
        )
    return speed


def parse_timeline_contract(payload: Mapping[str, Any]) -> TimelineSnapshot:
    if payload.get("schema_version") != "playback-timeline.v1":
        raise TimelineContractError("unsupported playback timeline schema")
    duration = _finite(payload.get("duration_seconds"), "duration_seconds")
    if duration <= 0 or duration > MAX_DURATION_SECONDS:
        raise TimelineContractError("duration_seconds must be > 0 and <= 86400")
    position = _bounded_position(payload.get("position_seconds"), duration)
    speed = _bounded_speed(payload.get("speed"))
    try:
        state = PlaybackState(payload.get("state"))
    except ValueError as error:
        raise TimelineContractError("state must be stopped, paused, or playing") from error
    return TimelineSnapshot(duration, position, speed, state)


class PlaybackTimeline:
    """Deterministic state machine for a shared visualization/audio clock."""

    def __init__(self, duration_seconds: float, speed: float = 1.0) -> None:
        duration = _finite(duration_seconds, "duration_seconds")
        if duration <= 0 or duration > MAX_DURATION_SECONDS:
            raise TimelineContractError("duration_seconds must be > 0 and <= 86400")
        self._duration = duration
        self._position = 0.0
        self._speed = _bounded_speed(speed)
        self._state = PlaybackState.STOPPED

    def snapshot(self) -> TimelineSnapshot:
        return TimelineSnapshot(
            self._duration, self._position, self._speed, self._state
        )

    def play(self) -> TimelineSnapshot:
        if self._position >= self._duration - EPSILON:
            self._position = 0.0
        self._state = PlaybackState.PLAYING
        return self.snapshot()

    def pause(self) -> TimelineSnapshot:
        if self._state == PlaybackState.PLAYING:
            self._state = PlaybackState.PAUSED
        return self.snapshot()

    def resume(self) -> TimelineSnapshot:
        if self._position < self._duration - EPSILON:
            self._state = PlaybackState.PLAYING
        return self.snapshot()

    def stop(self) -> TimelineSnapshot:
        self._state = PlaybackState.STOPPED
        self._position = 0.0
        return self.snapshot()

    def restart(self) -> TimelineSnapshot:
        self._position = 0.0
        self._state = PlaybackState.PLAYING
        return self.snapshot()

    def seek(self, position_seconds: float) -> TimelineSnapshot:
        position = _bounded_position(position_seconds, self._duration)
        self._position = position
        if position >= self._duration - EPSILON:
            self._position = self._duration
            self._state = PlaybackState.PAUSED
        return self.snapshot()

    def set_speed(self, speed: float) -> TimelineSnapshot:
        self._speed = _bounded_speed(speed)
        return self.snapshot()

    def advance(self, elapsed_seconds: float) -> TimelineSnapshot:
        elapsed = _finite(elapsed_seconds, "elapsed_seconds")
        if elapsed < 0:
            raise TimelineContractError("elapsed_seconds must be non-negative")
        if self._state != PlaybackState.PLAYING or elapsed == 0:
            return self.snapshot()
        self._position = min(
            self._duration, self._position + elapsed * self._speed
        )
        if self._position >= self._duration - EPSILON:
            self._position = self._duration
            self._state = PlaybackState.PAUSED
        return self.snapshot()
