"""GUI-independent sheet and playback types."""
from dataclasses import dataclass
from enum import Enum

MIN_EVENT_HOLD_MS = 5
MAX_EVENT_HOLD_MS = 60_000


class EventKind(str, Enum):
    NOTE = "NOTE"
    CHORD = "CHORD"
    FAST_SEQUENCE = "FAST_SEQUENCE"
    PAUSE = "PAUSE"
    TEMPO = "TEMPO"
    STEP = "STEP"
    DELAY = "DELAY"
    WAIT = "WAIT"
    RAMP = "RAMP"
    RESET = "RESET"


@dataclass(frozen=True, slots=True)
class SheetEvent:
    kind: EventKind
    keys: tuple[int, ...]
    source_start: int
    source_end: int
    pause_count: int = 0
    hold_ms: float | None = None
    key_holds_ms: tuple[float | None, ...] = ()
    timing_value: float | None = None
    timing_span: float | None = None


@dataclass(frozen=True, slots=True)
class ParsedSheet:
    events: tuple[SheetEvent, ...]
    source: str


@dataclass(frozen=True, slots=True)
class PlanEvent:
    offset_ms: float
    kind: EventKind
    keys: tuple[int, ...]
    source_start: int
    source_end: int
    hold_ms: float | None = None


@dataclass(frozen=True, slots=True)
class PlaybackPlan:
    events: tuple[PlanEvent, ...]
    duration_ms: float
