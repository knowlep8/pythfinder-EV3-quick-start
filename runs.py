"""
Your competition code goes here.

Each run is a plain function. The list you hand to RunSelector decides which
letter starts which run: the first is A, the second B, and so on. Press CENTER
on the hub to start the letter shown; the selector moves to the next one by
itself when the run finishes.
"""

from pybricks.tools import wait

from constants import zeroBeforeEveryRun
from robot import Robot
from run_selector import RunSelector

# Runs downloaded from the web planner. Each file has its own run(core).
# Imported under a different name from the function below that drives it --
# `import run_a` and `def run_a()` would be the same name, and the function
# would replace the module.
import run_a as planned_a
import run_b as planned_b
import run_c as planned_c
import run_square


core = Robot()


# --- optional hooks, run around every single run ----------------------------
def start_run():
    if zeroBeforeEveryRun:
        core.zero()


def stop_run():
    # A run's last move leaves the DriveBase holding its position and heading,
    # so it would fight you while you line up the next run. stop() lets the
    # wheels coast; the next run's configure()/set_heading() takes over again.
    core.drive_base.stop()


# --- one function per run ---------------------------------------------------
def run_a():
    planned_a.run(core)


def run_b():
    planned_b.run(core)


def run_c():
    planned_c.run(core)


def run_d():
    run_square.run(core)


# --- wire it up -------------------------------------------------------------
# wrap=True cycles back to A after the last run.
# Set one_time_use=True to have each letter disappear once it has been run,
# which is usually what you want during a real match.
selector = RunSelector(
    core,
    runs=[run_a, run_b, run_c, run_d],
    before=start_run,
    after=stop_run,
    wrap=True,
    one_time_use=False,
)
