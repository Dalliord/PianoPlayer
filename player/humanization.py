"""Small performance variations around the score, without cumulative tempo drift."""
import math
import random

from player.models import MAX_EVENT_HOLD_MS, MIN_EVENT_HOLD_MS, EventKind, PlanEvent, PlaybackPlan


def humanize_plan(plan: PlaybackPlan, note_delay_ms: int, key_hold_ms: int,
                  *, seed: int | None = None) -> PlaybackPlan:
    """Bake a fresh performance once per Play; pause/resume keeps this snapshot.

    Onset variation is bounded by 6% of Note Delay, 10 ms, and local spacing.
    Chords arrive in at most three small groups over at most 6 ms. Holds vary
    independently by up to 7% (at least 2 ms), within the public 5–200 ms range.
    Explicit sheet holds retain their written duration, including long sustains.
    Long breaths and the score's duration are anchored, not random walks.
    """
    if not 20 <= note_delay_ms <= 500:
        raise ValueError("Note Delay must be 20–500 ms")
    if not 5 <= key_hold_ms <= 200:
        raise ValueError("Key Hold Time must be 5–200 ms")
    if not math.isfinite(plan.duration_ms) or plan.duration_ms < 0:
        raise ValueError("Invalid plan duration")
    previous = -1.0
    for event in plan.events:
        if not math.isfinite(event.offset_ms) or not 0 <= event.offset_ms <= plan.duration_ms or event.offset_ms < previous:
            raise ValueError("Invalid plan offset")
        previous = event.offset_ms
    sounding = [event for event in plan.events if event.keys]
    if not sounding:
        return plan

    rng = random.Random(seed)
    result = [event for event in plan.events if not event.keys]
    limit = min(10.0, note_delay_ms * 0.06)
    hold_range = max(2.0, key_hold_ms * 0.07)
    for index, event in enumerate(sounding):
        explicit_hold = event.hold_ms
        if explicit_hold is not None and (not math.isfinite(explicit_hold)
                or not MIN_EVENT_HOLD_MS <= explicit_hold <= MAX_EVENT_HOLD_MS):
            raise ValueError("Invalid sheet hold")
        minimum_hold = explicit_hold if explicit_hold is not None else max(5.0, key_hold_ms - hold_range)
        before = event.offset_ms - sounding[index - 1].offset_ms if index else event.offset_ms
        after = ((sounding[index + 1].offset_ms if index + 1 < len(sounding) else plan.duration_ms)
                 - event.offset_ms)
        amplitude = min(limit, before * 0.18, after * 0.18)
        # Keep entrances after long rests exactly on their written downbeat.
        if index == 0 or before - key_hold_ms >= max(100.0, note_delay_ms * 0.75):
            amplitude = 0.0
        shift = rng.triangular(-amplitude, amplitude, 0) if amplitude else 0.0
        if event.offset_ms + minimum_hold > plan.duration_ms:
            raise ValueError("Plan duration cannot contain the requested hold")
        onset = min(max(0.0, event.offset_ms + shift), plan.duration_ms - minimum_hold)

        keys = tuple(dict.fromkeys(event.keys))
        spread = min(6.0, note_delay_ms * 0.07, after * 0.12)
        count = min(3, len(keys)) if spread >= 0.2 else 1
        offsets = [0.0] + sorted(rng.uniform(spread * 0.2, spread) for _ in range(count - 1))
        for group in range(count):
            chunk = keys[group * len(keys) // count:(group + 1) * len(keys) // count]
            when = round(min(onset + offsets[group], plan.duration_ms - minimum_hold), 3)
            if explicit_hold is not None:
                hold = explicit_hold
            else:
                hold = key_hold_ms + rng.triangular(-hold_range, hold_range, 0)
                hold = round(min(max(5.0, hold), 200.0, plan.duration_ms - when), 3)
            kind = EventKind.NOTE if len(chunk) == 1 else EventKind.CHORD
            result.append(PlanEvent(when, kind, chunk, event.source_start, event.source_end, hold))
    result.sort(key=lambda event: (event.offset_ms, event.source_start, event.source_end))
    return PlaybackPlan(tuple(result), plan.duration_ms)
