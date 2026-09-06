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
from trajectory import Trajectory

# Trajectories are generated on the PC -- see tools/txt_to_py.py.
import traj_test


core = Robot()

trajectory1 = Trajectory(traj_test)


# --- optional hooks, run around every single run ----------------------------
def start_run():
    if zeroBeforeEveryRun:
        core.zero()


def stop_run():
    ...


# --- one function per run ---------------------------------------------------
def run_a():
    trajectory1.follow(core)


def run_b():
    wait(1000)


def run_c():
    wait(1000)


# --- wire it up -------------------------------------------------------------
# wrap=True cycles back to A after the last run.
# Set one_time_use=True to have each letter disappear once it has been run,
# which is usually what you want during a real match.
selector = RunSelector(
    core,
    runs=[run_a, run_b, run_c],
    before=start_run,
    after=stop_run,
    wrap=True,
    one_time_use=False,
)
