"""A score clock with exact fractional beats and analytically integrated ramps."""
import math


class ScoreClock:
    def __init__(self, base_delay: float):
        self.base_delay = base_delay
        self.reset()

    def reset(self):
        self.delay = self.base_delay
        self.bpm = 60_000 / (self.base_delay * 4)
        self.step = 0.25
        self.remaining = 0.0
        self.slope = 0.0

    def tempo(self, bpm):
        self.bpm = bpm
        self.delay = None
        self.remaining = 0.0

    def subdivision(self, beats):
        self.step = beats
        self.delay = None

    def interval(self, milliseconds):
        self.delay = milliseconds
        self.remaining = 0.0
        if milliseconds > 0:
            self.bpm = 60_000 * self.step / milliseconds

    def ramp(self, target, beats):
        self.delay = None
        self.slope = (target - self.bpm) / beats
        self.remaining = beats

    def advance(self, units=1.0):
        if self.delay is not None:
            return units * self.delay
        beats = units * self.step
        elapsed = 0.0
        if self.remaining > 1e-12:
            part = min(beats, self.remaining)
            elapsed = (60_000 * part / self.bpm if abs(self.slope) < 1e-12 else
                       60_000 / self.slope * math.log1p(self.slope * part / self.bpm))
            self.bpm += self.slope * part
            self.remaining = max(0.0, self.remaining - part)
            beats -= part
        return elapsed + 60_000 * beats / self.bpm
