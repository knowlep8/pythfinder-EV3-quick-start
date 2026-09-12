"""A run in the shape the web planner writes, small enough to read.

The planner produces exactly this file: the trajectory data, the attachment
motor code, and a run() that ties them together. This one is hand-written with
four states of nonsense data so the shape is legible -- a real one carries
thousands, and is not worth reading.

Put it beside the other files in the Pybricks project and add it to runs.py:

    import example_run
    ...
    runs=[example_run.run, ...]

The three numbers and the bytes are what the planner fills in:

    STEPS    how many milliseconds each state lasts
    MARKERS  when each action fires, in milliseconds
    COUNT    how many states there are
    DATA     COUNT x 3 little-endian int16: left*100, right*100, heading*10
"""

from trajectory import Trajectory


STEPS = 6
MARKERS = (12, 18)
COUNT = 4

# four states: forward, forward, forward, stop -- at 50% on both wheels,
# holding a heading of 0
DATA = (
    b'\x88\x13\x88\x13\x00\x00'
    b'\x88\x13\x88\x13\x00\x00'
    b'\x88\x13\x88\x13\x00\x00'
    b'\x00\x00\x00\x00\x00\x00'
)


def _arm_down(core):
    """12ms in. Keep it short: markers run on the loop that drives."""
    if core.leftTask is not None:
        core.leftTask.run(500)


def _arm_up(core):
    """18ms in, which is the last state."""
    if core.leftTask is not None:
        core.leftTask.run(-500)


def run(core):
    """Drive this run. The only thing runs.py needs to call."""
    trajectory = Trajectory.fromValues(STEPS, MARKERS, COUNT, DATA)

    # The order here is the order the actions HAPPEN, which is the order the
    # planner writes them in -- not the order they were added to the run.
    trajectory.withMarkers((
        lambda: _arm_down(core),
        lambda: _arm_up(core),
    ))

    trajectory.follow(core)
