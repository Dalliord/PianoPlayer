"""Sheet notation: groups, pauses and an optional <milliseconds> hold suffix."""
from fractions import Fraction
import re
from player.models import MAX_EVENT_HOLD_MS, MIN_EVENT_HOLD_MS, EventKind, ParsedSheet, SheetEvent


class SheetSyntaxError(ValueError):
    def __init__(self, message: str, start: int, end: int):
        super().__init__(message)
        self.start = start
        self.end = end


class SheetParser:
    def parse(self, source: str) -> ParsedSheet:
        events: list[SheetEvent] = []
        index = 0
        while index < len(source):
            char = source[index]
            if char.isspace():
                index += 1
                continue
            start = index
            if char == "|":
                closing = source.find("|", index + 1)
                if closing == -1:
                    raise SheetSyntaxError("Не закрыта команда тайминга |…|.", start, len(source))
                index = closing + 1
                events.append(self._command(source[start+1:closing], start, index))
            elif char in "[{":
                closing = "]" if char == "[" else "}"
                kind = EventKind.CHORD if char == "[" else EventKind.FAST_SEQUENCE
                index += 1
                keys: list[int] = []
                key_holds: list[float | None] = []
                while index < len(source) and source[index] != closing:
                    inner = source[index]
                    if inner in "[]{}":
                        raise SheetSyntaxError("Вложенные или несовпадающие скобки.", index, index + 1)
                    if inner in "<>":
                        raise SheetSyntaxError("Удержание указывается сразу после клавиши: [a<1000>sd].", index, index + 1)
                    if not inner.isspace():
                        self._validate_key(inner, index)
                        keys.append(ord(inner))
                        index, key_hold = self._read_hold(source, index + 1)
                        key_holds.append(key_hold)
                    else:
                        index += 1
                if index == len(source):
                    raise SheetSyntaxError(f"Не закрыта скобка {char}.", start, len(source))
                if not keys:
                    raise SheetSyntaxError("Пустая группа.", start, index + 1)
                index += 1
                index, hold = self._read_hold(source, index)
                events.append(SheetEvent(kind, tuple(keys), start, index, hold_ms=hold,
                                         key_holds_ms=tuple(key_holds) if any(h is not None for h in key_holds) else ()))
            elif char in "]}>":
                raise SheetSyntaxError("Закрывающая скобка без открывающей.", index, index + 1)
            elif char == "<":
                raise SheetSyntaxError("Удержание указывается сразу после ноты или группы: a<1000>.", index, index + 1)
            elif char == "-":
                while index < len(source) and source[index] == "-":
                    index += 1
                events.append(SheetEvent(EventKind.PAUSE, (), start, index, index - start))
            else:
                self._validate_key(char, index)
                index += 1
                index, hold = self._read_hold(source, index)
                events.append(SheetEvent(EventKind.NOTE, (ord(char),), start, index, hold_ms=hold))
        return ParsedSheet(tuple(events), source)

    @staticmethod
    def _read_hold(source: str, index: int) -> tuple[int, float | None]:
        if index == len(source) or source[index] != "<":
            return index, None
        closing = source.find(">", index + 1)
        if closing == -1:
            raise SheetSyntaxError("Не закрыта длительность удержания <…>.", index, len(source))
        value = source[index + 1:closing]
        if (not re.fullmatch(r"[0-9]{1,5}(?:\.[0-9]{1,3})?", value)
                or not MIN_EVENT_HOLD_MS <= float(value) <= MAX_EVENT_HOLD_MS):
            raise SheetSyntaxError("Удержание: от 5 до 60000 ms, например <1000> или <125.5>.", index, closing + 1)
        return closing + 1, float(value) if "." in value else int(value)

    @staticmethod
    def _command(text: str, start: int, end: int) -> SheetEvent:
        command, separator, raw = text.strip().partition("=")
        try:
            if command == "reset" and not separator:
                return SheetEvent(EventKind.RESET, (), start, end)
            kinds = {"bpm": EventKind.TEMPO, "step": EventKind.STEP, "delay": EventKind.DELAY,
                     "wait": EventKind.WAIT, "ramp": EventKind.RAMP}
            if command not in kinds or not separator:
                raise ValueError
            values = [value.strip() for value in raw.split(",")]
            if len(values) != (2 if command == "ramp" else 1):
                raise ValueError
            if command == "step":
                if not re.fullmatch(r"[0-9]{1,3}(?:/[0-9]{1,3}|\.[0-9]{1,6})?", values[0]):
                    raise ValueError
                value = float(Fraction(values[0]))
                if not 1/128 <= value <= 16:
                    raise ValueError
            else:
                if any(not re.fullmatch(r"[0-9]{1,7}(?:\.[0-9]{1,3})?", value) for value in values):
                    raise ValueError
                value = float(values[0])
                low, high = {"bpm": (10, 1000), "ramp": (10, 1000),
                             "wait": (0, 3_600_000), "delay": (0, 60_000)}[command]
                if not low <= value <= high:
                    raise ValueError
            span = float(values[1]) if command == "ramp" else None
            if span is not None and not 0.001 <= span <= 1024:
                raise ValueError
            return SheetEvent(kinds[command], (), start, end, timing_value=value, timing_span=span)
        except (ValueError, ZeroDivisionError):
            raise SheetSyntaxError("Команды: |bpm=120|, |step=1/3|, |delay=75.5|, |wait=250|, |ramp=180,8|, |reset|.", start, end) from None

    @staticmethod
    def _validate_key(char: str, position: int) -> None:
        if char == "|":
            raise SheetSyntaxError("Команды |…| указываются вне нотных групп.", position, position + 1)
        # Printable US keyboard characters; no arbitrary Unicode text injection.
        if not 33 <= ord(char) <= 126:
            raise SheetSyntaxError(f"Неподдерживаемая клавиша: {char!r}.", position, position + 1)
