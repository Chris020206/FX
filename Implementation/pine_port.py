"""Line-by-line Python port of `Detection_Methods/order_blocks_v2 (26.07.17).pine` (v2.2).

M1 — translation only. No detection logic is invented, improved, or simplified here.
Comments of the form (Pine L###) reference line numbers in the source .pine file.
Display-only inputs (colors, border width/style, extendBars, alerts) have no behavioral
role in detection/lifecycle and are not carried across; everything that affects which
boxes exist, their bounds, activation, mitigation, and removal is.

Semantics choices that Pine does not spell out in the source text are listed in
`Implementation/M1_PORT_NOTES.md` (pivot tie handling, RMA seeding, session-string
boundary semantics) — verify them at gate time against TradingView output.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

# ── INPUTS (Pine L17-73) — defaults carried verbatim ─────────────────────────
PIVOT_K = 2                   # pivotK (L18)
STACK_DEPTH = 0               # stackDepth (L20), off by default
DISP_GATE_ATR = 1.5           # dispGateATR (L22)
DISP_GATE_BARS = 3            # dispGateBars (L24)
MIN_ZONE_ATR = 0.75           # minZoneATR (L26)

ENABLE_V2 = True              # enableV2 (L30)
V2_WINDOW = (15 * 60 + 40, 16 * 60 + 5)    # v2Window "1540-1605" (L32)
KEEP_V2_VISIBLE = True        # keepV2Visible (L34)

MAX_BOXES_SHOWN = 30          # maxBoxesShown (L42), per side

REQUIRE_ACTIVATION = True     # requireActivation (L45)
ACTIVATION_METHOD = "Wick"    # activationMethod (L47)
ACTIVATION_BUFFER_ATR = 0.0   # activationBufferATR (L49)

MITIGATION_METHOD = "Wick"    # mitigationMethod (L53)
MITIGATION_FILL_PCT = 25.0    # mitigationFillPct (L55)

USE_SESSION_FILTER = True     # useSessionFilter (L59)
SESSION_WINDOW = (15 * 60 + 15, 16 * 60 + 15)  # sessionWindow "1515-1615" (L61)
SESSION_TZ = ZoneInfo("Europe/London")         # sessionTZ (L62)
USE_PROXIMITY_FILTER = False  # useProximityFilter (L64)
PROXIMITY_ATR = 1.5           # proximityATR (L66)
MAX_AGE_HOURS = 3.0           # maxAgeHours (L68)

ATR_LEN = 14


# ── STATE (Pine L76-100) ─────────────────────────────────────────────────────
@dataclass
class OB:
    top: float
    bot: float
    is_bull: bool
    mitigated: bool
    activated: bool
    start_bar: int            # startBar — absolute origin bar index
    origin_time: int          # originTime — origin bar open, epoch seconds
    created_bar: int          # createdBar
    is_v2: bool               # isV2 — origin candle sits inside the V2 formation window
    act_edge: Optional[float] # actEdge — None = standard activation; float = strict V2
    # ── port-only lifecycle record (no behavioral role; for gate comparison) ──
    path: str = "pivot"                    # which code path created it
    created_time: int = 0
    activated_time: Optional[int] = None
    removed_time: Optional[int] = None
    removed_reason: Optional[str] = None   # mitigated / day_boundary / max_age /
                                           # evicted_max_boxes / alive_at_end
    shown_in_window: bool = False          # visible on >=1 display-window bar


@dataclass
class Pending:                # (Pine L94-96)
    origin_bar: int
    is_bull: bool


class Bars:
    """OHLC series. `t` is bar OPEN time in epoch seconds (raw CSV timestamps)."""

    def __init__(self, t, o, h, l, c):
        self.t, self.o, self.h, self.l, self.c = t, o, h, l, c
        self.n = len(t)
        self.atr = self._atr14()
        self._minute_cache = [self._london_minute(ts) for ts in t]

    def _atr14(self) -> List[float]:
        """ta.atr(14) = ta.rma(true range, 14). RMA is Wilder's smoothing seeded
        with the SMA of the first 14 TR values; NaN before bar index 13.
        First bar's TR is high-low (no prior close)."""
        tr = [self.h[0] - self.l[0]]
        for i in range(1, self.n):
            tr.append(max(self.h[i] - self.l[i],
                          abs(self.h[i] - self.c[i - 1]),
                          abs(self.l[i] - self.c[i - 1])))
        atr = [math.nan] * self.n
        if self.n >= ATR_LEN:
            atr[ATR_LEN - 1] = sum(tr[:ATR_LEN]) / ATR_LEN
            for i in range(ATR_LEN, self.n):
                atr[i] = (atr[i - 1] * (ATR_LEN - 1) + tr[i]) / ATR_LEN
        return atr

    def _london_minute(self, ts: int) -> int:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(SESSION_TZ)
        return dt.hour * 60 + dt.minute

    def in_window(self, i: int, window) -> bool:
        """Pine `time(timeframe.period, session, tz)` non-na test: the bar's OPEN
        time falls in [start, end) — end exclusive for open times, per the
        v2Window tooltip (L33: '1605 is needed to include the candle opening at
        16:00')."""
        m = self._minute_cache[i]
        return window[0] <= m < window[1]

    def london_date(self, ts: int):
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(SESSION_TZ).date()


class Detector:
    def __init__(self, bars: Bars):
        self.b = bars
        self.bull_boxes: List[OB] = []   # (Pine L98)
        self.bear_boxes: List[OB] = []   # (Pine L99)
        self.pending: List[Pending] = [] # (Pine L100)
        self.all_boxes: List[OB] = []    # port-only: every box ever created

    # ── OB CREATION (Pine L115-144) ──────────────────────────────────────────
    def origin_exists(self, abs_bar: int, is_bull: bool) -> bool:
        arr = self.bull_boxes if is_bull else self.bear_boxes
        return any(ob.start_bar == abs_bar for ob in arr)

    def create_ob(self, i: int, bar_offset: int, is_bull: bool,
                  v2_act_edge: Optional[float], path: str) -> None:
        abs_bar = i - bar_offset
        if self.origin_exists(abs_bar, is_bull):
            return
        b = self.b
        ob = OB(top=b.h[abs_bar], bot=b.l[abs_bar], is_bull=is_bull,
                mitigated=False, activated=not REQUIRE_ACTIVATION,
                start_bar=abs_bar, origin_time=b.t[abs_bar], created_bar=i,
                is_v2=b.in_window(abs_bar, V2_WINDOW),  # isV2 = inV2Window[barOffset] (L129)
                act_edge=v2_act_edge, path=path, created_time=b.t[i])
        arr = self.bull_boxes if is_bull else self.bear_boxes
        arr.append(ob)
        self.all_boxes.append(ob)
        if len(arr) > MAX_BOXES_SHOWN:            # (Pine L137-138 / L141-142)
            evicted = arr.pop(0)
            evicted.removed_reason = "evicted_max_boxes"
            evicted.removed_time = b.t[i]

    # ── QUALIFYING-IMPULSE GATE (Pine L146-186) ──────────────────────────────
    def zone_ok(self, i: int, origin_off: int) -> bool:
        if MIN_ZONE_ATR <= 0:
            return True
        j = i - origin_off
        atr = self.b.atr[j]
        if math.isnan(atr):                      # na comparison is false in Pine
            return False
        return (self.b.h[j] - self.b.l[j]) >= MIN_ZONE_ATR * atr

    def disp_passed_at(self, i: int, origin_off: int, candle_off: int,
                       is_bull: bool) -> bool:
        """ATR referenced at the ORIGIN bar — threshold fixed at formation time
        (Pine L159-163)."""
        j = i - origin_off
        atr = self.b.atr[j]
        if math.isnan(atr):
            return False
        need = DISP_GATE_ATR * atr
        if is_bull:
            return (self.b.c[i - candle_off] - self.b.l[j]) >= need
        return (self.b.h[j] - self.b.c[i - candle_off]) >= need

    def gate_verdict(self, i: int, is_bull: bool) -> int:
        """1 = create now, 0 = park as pending, -1 = reject (Pine L167-186)."""
        if not self.zone_ok(i, PIVOT_K):
            return -1
        if DISP_GATE_ATR <= 0:
            return 1
        passed = False
        for m in range(1, min(DISP_GATE_BARS, PIVOT_K) + 1):
            if self.disp_passed_at(i, PIVOT_K, PIVOT_K - m, is_bull):
                passed = True
        if passed:
            return 1
        if PIVOT_K >= DISP_GATE_BARS:
            return -1
        return 0

    def create_with_stack(self, i: int, origin_off: int, is_bull: bool,
                          path: str) -> None:
        """(Pine L190-202). Impulse gate NOT re-evaluated per backfilled candle —
        a passing pivot validates its run as one zone."""
        self.create_ob(i, origin_off, is_bull, None, path)
        if STACK_DEPTH > 0:
            b = self.b
            for t_ in range(1, STACK_DEPTH + 1):
                if is_bull:
                    step_ok = b.l[i - (origin_off + t_)] > b.l[i - (origin_off + t_ - 1)]
                else:
                    step_ok = b.h[i - (origin_off + t_)] < b.h[i - (origin_off + t_ - 1)]
                if step_ok:
                    self.create_ob(i, origin_off + t_, is_bull, None, "stack")
                else:
                    break

    # ── PIVOT DETECTION (Pine L106-109) ──────────────────────────────────────
    # ta.pivothigh/pivotlow(K, K): candidate at i-K must be a STRICT extreme vs.
    # the K bars on each side. Tie handling is not stated in the Pine source —
    # implemented as strict on both sides; flagged in M1_PORT_NOTES.md.
    def pivot_high(self, i: int) -> bool:
        if i < 2 * PIVOT_K:
            return False
        j = i - PIVOT_K
        v = self.b.h[j]
        return all(v > self.b.h[k] for k in range(i - 2 * PIVOT_K, i + 1) if k != j)

    def pivot_low(self, i: int) -> bool:
        if i < 2 * PIVOT_K:
            return False
        j = i - PIVOT_K
        v = self.b.l[j]
        return all(v < self.b.l[k] for k in range(i - 2 * PIVOT_K, i + 1) if k != j)

    # ── ACTIVATION (Pine L261-275) ───────────────────────────────────────────
    def check_activation(self, i: int, ob: OB) -> bool:
        b = self.b
        if ob.act_edge is not None:
            # strict Variation 2 activation: candle CLOSE beyond the
            # confirmation candle's extreme (Pine L263-266)
            return b.c[i] > ob.act_edge if ob.is_bull else b.c[i] < ob.act_edge
        atr = b.atr[i]
        buffer = ACTIVATION_BUFFER_ATR * (0.0 if math.isnan(atr) else atr)
        if ob.is_bull:
            probe = b.h[i] if ACTIVATION_METHOD == "Wick" else b.c[i]
            return probe > ob.top + buffer
        probe = b.l[i] if ACTIVATION_METHOD == "Wick" else b.c[i]
        return probe < ob.bot - buffer

    # ── MITIGATION (Pine L278-288) ───────────────────────────────────────────
    def check_mitigation(self, i: int, ob: OB) -> bool:
        b = self.b
        zone_height = ob.top - ob.bot
        if ob.is_bull:
            threshold = ob.top - zone_height * (MITIGATION_FILL_PCT / 100.0)
            probe = b.l[i] if MITIGATION_METHOD == "Wick" else b.c[i]
            return probe <= threshold
        threshold = ob.bot + zone_height * (MITIGATION_FILL_PCT / 100.0)
        probe = b.h[i] if MITIGATION_METHOD == "Wick" else b.c[i]
        return probe >= threshold

    def process_array(self, i: int, arr: List[OB]) -> None:
        """(Pine L290-314). box.set_right calls are display-only and dropped."""
        for idx in range(len(arr) - 1, -1, -1):
            ob = arr[idx]
            if ob.mitigated:
                continue
            if not ob.activated:
                if self.check_activation(i, ob):
                    ob.activated = True
                    ob.activated_time = self.b.t[i]
            elif ob.created_bar == i:
                # never mitigate on the instantiation bar (Pine L301-305)
                pass
            elif self.check_mitigation(i, ob):
                ob.mitigated = True
                ob.removed_reason = "mitigated"
                ob.removed_time = self.b.t[i]
                del arr[idx]

    # ── CLEANUP (Pine L319-347) ──────────────────────────────────────────────
    def cleanup_day(self, i: int, arr: List[OB]) -> None:
        # tz = sessionTZ when useSessionFilter, else exchange tz (Pine L320-322)
        today = self.b.london_date(self.b.t[i])
        for idx in range(len(arr) - 1, -1, -1):
            ob = arr[idx]
            if self.b.london_date(ob.origin_time) != today:
                ob.removed_reason = "day_boundary"
                ob.removed_time = self.b.t[i]
                del arr[idx]

    def cleanup_age(self, i: int, arr: List[OB]) -> None:
        if MAX_AGE_HOURS <= 0:
            return
        age_limit = MAX_AGE_HOURS * 3600  # timestamps in seconds, Pine uses ms
        for idx in range(len(arr) - 1, -1, -1):
            ob = arr[idx]
            if (self.b.t[i] - ob.origin_time) > age_limit:
                ob.removed_reason = "max_age"
                ob.removed_time = self.b.t[i]
                del arr[idx]

    # ── VISIBILITY (Pine L349-373) — recorded, nothing is drawn ─────────────
    def zone_distance(self, i: int, ob: OB) -> float:
        c = self.b.c[i]
        if ob.bot <= c <= ob.top:
            return 0.0
        return min(abs(c - ob.top), abs(c - ob.bot))

    def apply_visibility(self, i: int, arr: List[OB], in_session: bool) -> None:
        """Pine draws a box when (inSession or keepV2Visible-and-isV2) and
        nearEnough (L354-370). Nothing is drawn here; we record the metric the
        gate cares about — was the box visible on at least one bar whose open
        sits in the display window (the '3.2 boxes/day in-window' count). The
        V2 after-window extension changes display outside the window only, so
        it cannot affect this flag."""
        if not in_session:
            return
        for ob in arr:
            atr = self.b.atr[i]
            near_enough = (not USE_PROXIMITY_FILTER
                           or (not math.isnan(atr)
                               and self.zone_distance(i, ob) <= PROXIMITY_ATR * atr))
            if near_enough:
                ob.shown_in_window = True

    # ── MAIN LOOP — one Pine execution per bar, in source order ─────────────
    def run(self) -> List[OB]:
        b = self.b
        for i in range(b.n):
            in_session = (not USE_SESSION_FILTER) or b.in_window(i, SESSION_WINDOW)

            # VARIATION 2 DETECTION (Pine L219-225)
            if ENABLE_V2 and i > 2 and b.in_window(i - 1, V2_WINDOW):
                if b.l[i - 1] < b.l[i - 2] and b.c[i - 1] < b.o[i - 1] and b.c[i] > b.h[i - 1]:
                    self.create_ob(i, 1, True, b.h[i], "v2")
                if b.h[i - 1] > b.h[i - 2] and b.c[i - 1] > b.o[i - 1] and b.c[i] < b.l[i - 1]:
                    self.create_ob(i, 1, False, b.l[i], "v2")

            # PENDING RE-CHECK (Pine L228-238) — before any pivot confirming this bar
            for idx in range(len(self.pending) - 1, -1, -1):
                pc = self.pending[idx]
                age = i - pc.origin_bar
                if age <= DISP_GATE_BARS and self.disp_passed_at(i, age, 0, pc.is_bull):
                    self.create_with_stack(i, age, pc.is_bull, "pivot_delayed")
                    del self.pending[idx]
                elif age >= DISP_GATE_BARS:
                    del self.pending[idx]

            # PIVOT CREATION (Pine L240-258)
            pl = self.pivot_low(i)
            ph = self.pivot_high(i)
            dual_tagged = pl and ph
            if not dual_tagged and pl:
                v = self.gate_verdict(i, True)
                if v == 1:
                    self.create_with_stack(i, PIVOT_K, True, "pivot")
                elif v == 0:
                    self.pending.append(Pending(i - PIVOT_K, True))
            if not dual_tagged and ph:
                v = self.gate_verdict(i, False)
                if v == 1:
                    self.create_with_stack(i, PIVOT_K, False, "pivot")
                elif v == 0:
                    self.pending.append(Pending(i - PIVOT_K, False))

            # ACTIVATION / MITIGATION (Pine L316-317)
            self.process_array(i, self.bull_boxes)
            self.process_array(i, self.bear_boxes)

            # DAY-BOUNDARY CLEANUP (Pine L332-333)
            self.cleanup_day(i, self.bull_boxes)
            self.cleanup_day(i, self.bear_boxes)

            # MAX-AGE CLEANUP (Pine L346-347)
            self.cleanup_age(i, self.bull_boxes)
            self.cleanup_age(i, self.bear_boxes)

            # SESSION VISIBILITY (Pine L372-373)
            self.apply_visibility(i, self.bull_boxes, in_session)
            self.apply_visibility(i, self.bear_boxes, in_session)

        for arr in (self.bull_boxes, self.bear_boxes):
            for ob in arr:
                if ob.removed_reason is None:
                    ob.removed_reason = "alive_at_end"
        return self.all_boxes
