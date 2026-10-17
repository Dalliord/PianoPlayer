"""Build absolute note onsets independently from physical key hold time."""
from pathlib import Path
import math
from player.models import MAX_EVENT_HOLD_MS, MIN_EVENT_HOLD_MS, EventKind, ParsedSheet, PlanEvent, PlaybackPlan
from player.tempo import ScoreClock

FAST_RATIO = 0.35


def build_plan(sheet: ParsedSheet, note_delay_ms: int = 100,
               key_hold_ms: int = 35) -> PlaybackPlan:
    if not 20 <= note_delay_ms <= 500:
        raise ValueError("Note Delay must be 20–500 ms")
    if not 5 <= key_hold_ms <= 200:
        raise ValueError("Key Hold Time must be 5–200 ms")
    events: list[PlanEvent] = []
    offset = 0.0
    last_release = 0.0
    clock = ScoreClock(note_delay_ms)
    for event in sheet.events:
        if event.kind == EventKind.TEMPO:
            clock.tempo(event.timing_value)
            continue
        if event.kind == EventKind.STEP:
            clock.subdivision(event.timing_value)
            continue
        if event.kind == EventKind.DELAY:
            clock.interval(event.timing_value)
            continue
        if event.kind == EventKind.RAMP:
            clock.ramp(event.timing_value, event.timing_span)
            continue
        if event.kind == EventKind.RESET:
            clock.reset()
            continue
        if event.kind == EventKind.WAIT:
            events.append(PlanEvent(offset, EventKind.PAUSE, (), event.source_start, event.source_end))
            offset += event.timing_value
            if offset > 3_600_000:
                raise ValueError("Максимальная длительность партитуры — 1 час.")
            continue
        hold = event.hold_ms if event.hold_ms is not None else key_hold_ms
        if not math.isfinite(hold) or not MIN_EVENT_HOLD_MS <= hold <= MAX_EVENT_HOLD_MS:
            raise ValueError("Invalid sheet hold")
        if event.key_holds_ms and len(event.key_holds_ms) != len(event.keys):
            raise ValueError("Individual holds must match the group's keys")
        holds = tuple(value if value is not None else event.hold_ms
                      for value in event.key_holds_ms) if event.key_holds_ms else (event.hold_ms,) * len(event.keys)
        if any(value is not None and (not math.isfinite(value) or not MIN_EVENT_HOLD_MS <= value <= MAX_EVENT_HOLD_MS)
               for value in holds):
            raise ValueError("Invalid individual sheet hold")
        if event.kind == EventKind.PAUSE:
            events.append(PlanEvent(offset, event.kind, (), event.source_start, event.source_end))
            offset += clock.advance(event.pause_count)
        elif event.kind == EventKind.FAST_SEQUENCE:
            for index, key in enumerate(event.keys):
                events.append(PlanEvent(offset, EventKind.NOTE, (key,),
                                        event.source_start, event.source_end, holds[index]))
                last_release = max(last_release, offset + (holds[index] if holds[index] is not None else key_hold_ms))
                offset += clock.advance(FAST_RATIO if index < len(event.keys) - 1 else 1)
        else:
            # Simultaneous keys may have different release times. Each group
            # shares one onset and source span, so the score clock advances once.
            groups: dict[int | None, list[int]] = {}
            for key, value in zip(event.keys, holds):
                groups.setdefault(value, []).append(key)
            for value, keys in groups.items():
                events.append(PlanEvent(offset, event.kind, tuple(keys),
                                        event.source_start, event.source_end, value))
                last_release = max(last_release, offset + (value if value is not None else key_hold_ms))
            offset += clock.advance()
        if max(offset, last_release) > 3_600_000:
            raise ValueError("Максимальная длительность партитуры — 1 час.")
    return PlaybackPlan(tuple(events), max(offset, last_release))


def write_plan(plan: PlaybackPlan, path: Path, key_hold_ms: int) -> None:
    """TSV only contains numeric code points, never executable sheet text."""
    if not 5 <= key_hold_ms <= 200:
        raise ValueError("Key Hold Time must be 5–200 ms")
    version = 2 if any(event.hold_ms is not None for event in plan.events) else 1
    if any(event.hold_ms is not None and event.hold_ms > 200 for event in plan.events):
        version = 3
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"ROBLOXSHEETS\t{version}\t{key_hold_ms}\t{plan.duration_ms:.3f}\n")
        for event in plan.events:
            keys = ",".join(map(str, event.keys)) or "0"
            extra = ""
            if version >= 2:
                hold = 0 if event.kind == EventKind.PAUSE else (event.hold_ms if event.hold_ms is not None else key_hold_ms)
                if not math.isfinite(hold) or (event.kind != EventKind.PAUSE and not MIN_EVENT_HOLD_MS <= hold <= MAX_EVENT_HOLD_MS):
                    raise ValueError("Invalid event hold")
                extra = f"\t{hold:.3f}"
            stream.write(f"{event.offset_ms:.3f}\t{event.kind.value}\t{keys}\t"
                         f"{event.source_start}\t{event.source_end}{extra}\n")
