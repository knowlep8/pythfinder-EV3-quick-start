"""
Letter-based run selector for a SPIKE Prime hub.

The EV3 template bound one run to each direction button. The hub only has
LEFT, RIGHT and CENTER, so that scheme does not survive the port. Instead:

    - the 5x5 display shows the letter of the *armed* run (A, B, C, ...)
    - CENTER runs it; the letter stays lit while it runs
    - when the run returns, the selector auto-advances to the next letter
    - LEFT / RIGHT jog the selection without running anything, so you can
      skip ahead or go back and repeat one that misbehaved

During a clean match the technician only ever taps CENTER.

This is deliberately close to Pybricks' own hub_menu(), which cannot
auto-advance and so would need re-selecting between every run.
"""

from pybricks.parameters import Button, Icon
from pybricks.tools import wait

from constants import takeHandsOff, time_to_take_hands_off
from edge_detector import EdgeDetectorEx
from math_ex import sToMs

_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class RunSelector():

    def __init__(self, robot, runs, before=None, after=None,
                 labels=None, wrap=True, one_time_use=False):
        self.robot = robot
        self.hub = robot.hub
        self.led = robot.led_control

        self.runs = list(runs)          # zero-argument callables
        self.before = before
        self.after = after
        self.labels = labels            # optional list[str], one per run
        self.wrap = wrap
        self.one_time_use = one_time_use

        if not self.runs:
            raise Exception("RunSelector needs at least one run")

        self.index = 0
        self.finished = False
        self._completed = set()

        self._center = EdgeDetectorEx()
        self._left = EdgeDetectorEx()
        self._right = EdgeDetectorEx()

        self.led.not_started()
        self._render()

    # --- display ----------------------------------------------------------
    def _label(self, i):
        if self.labels is not None and i < len(self.labels):
            return self.labels[i]
        return _LETTERS[i] if i < len(_LETTERS) else "?"

    def _render(self):
        if self.finished:
            self.hub.display.icon(Icon.HAPPY)
        else:
            self.hub.display.char(self._label(self.index))

    # --- navigation -------------------------------------------------------
    def _next_index(self, start, delta):
        """First index after `start` that still has a run left to do."""
        n = len(self.runs)
        index = start

        for _ in range(n):
            index += delta

            if self.wrap:
                index %= n
            elif not 0 <= index < n:
                return None

            if index not in self._completed:
                return index

        return None

    def _step(self, delta):
        nxt = self._next_index(self.index, delta)

        if nxt is None:
            # Nothing left ahead means the program is done. Running off the
            # front just means "stay put".
            if delta > 0:
                self.finished = True
        else:
            self.index = nxt
            self.finished = False

        self._render()

    # --- main loop --------------------------------------------------------
    def update(self):
        pressed = self.hub.buttons.pressed()

        self._center.set(Button.CENTER in pressed)
        self._left.set(Button.LEFT in pressed)
        self._right.set(Button.RIGHT in pressed)

        self._center.update()
        self._left.update()
        self._right.update()

        if self._left.rising:
            self._step(-1)
        elif self._right.rising:
            self._step(+1)
        elif self._center.rising and not self.finished:
            self._execute()

    def run_forever(self, poll_ms=10):
        while True:
            self.update()
            wait(poll_ms)

    # --- execution --------------------------------------------------------
    def _execute(self):
        index = self.index

        if self.before is not None:
            self.before()

        if takeHandsOff:
            self.led.take_your_hands_off()
            wait(int(sToMs(time_to_take_hands_off)))

        self.led.in_progress()
        self._render()                       # keep the letter up while running

        self.runs[index]()                   # blocks until the run returns

        if self.after is not None:
            self.after()

        self.led.not_started()

        if self.one_time_use:
            self._completed.add(index)

        self._drain_center()
        self._step(+1)

    def _drain_center(self):
        """Ignore a CENTER press still being held when the run ends."""
        while Button.CENTER in self.hub.buttons.pressed():
            wait(10)

        self._center.set(False)
        self._center.update()
