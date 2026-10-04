<p align="center" style="margin-bottom: 10px;">
      <img src="https://i.ibb.co/mHSpjdL/pyth-finder-logo-ev3-quickstart.png" alt="pyth-finder-logo" border="0">
</p>

![version_badge](https://img.shields.io/badge/alpha-0.0.4-006400)
![quickstart](https://img.shields.io/badge/SPIKE_Prime_implementation-006400)
![license](https://img.shields.io/badge/license-MIT-62e39e)

The hub side of [PythFinder][1] for the **LEGO SPIKE Prime / Robot Inventor
hub**, running [Pybricks][0]. Runs are planned in PythFinder's web planner,
downloaded as a short Python file, and driven here by Pybricks' own
`DriveBase`.

> Looking for the EV3 version? It lives on the `main` branch. This branch is a
> port, not a superset: the hub has no filesystem, no threading, and only three
> usable buttons, so several things work differently. See
> [What changed from the EV3 version](#what-changed-from-the-ev3-version).

# Installation

## Pybricks

Install the Pybricks firmware on your hub by following the
[**official guide**][0]. Everything here runs in the browser at
[code.pybricks.com][2] -- there is no VS Code extension for Pybricks, so the
usual workflow is to edit these files locally and upload them there.

Nothing needs installing on your computer: runs come from the web planner,
and every file here runs on the hub.

## This project

Clone the repo and check out this branch:

```bash
git clone https://github.com/omegacoreFLL/pythfinder-EV3-quick-start.git
cd pythfinder-EV3-quick-start
git checkout spike-port
```

In [code.pybricks.com][2], create a project and add each `.py` file from the
repository root. Pybricks bundles any module you `import` along with the file
you run, so they all travel to the hub together.

> **Files must sit flat, side by side.** Pybricks does not support
> subdirectories, which is why this branch has no `BetterClasses/`,
> `Controllers/` or `Settings/` folders.

<br/>

# Usage

## Setup

Open **`config.py`** and describe your robot:

```python
# how the hub is mounted
HUB_TOP_SIDE = Axis.Z
HUB_FRONT_SIDE = Axis.X

# motors -- the hub has six identical ports, A through F
LEFT_WHEEL_PORT = Port.F
RIGHT_WHEEL_PORT = Port.B
LEFT_TASK_PORT = Port.A
RIGHT_TASK_PORT = Port.E

# sensors go in those same A-F ports; None if you do not have one
COLOR_SENSOR_LEFT_PORT = None
COLOR_SENSOR_RIGHT_PORT = None
ATTACHMENT_COLOR_SENSOR_PORT = None

# flip one of these if a wheel spins backwards
LEFT_WHEEL_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_WHEEL_DIRECTION = Direction.CLOCKWISE

# measured with drivebase_test.py -- see below
WHEEL_DIAMETER_MM = 55.6
AXLE_TRACK_MM = 160.1
```

**Two wheel motors are required.** Task motors and color sensors are optional --
set a port to `None` if you do not have that part.

`HUB_TOP_SIDE` / `HUB_FRONT_SIDE` replace the EV3's external gyro and its four
orientation flags. Describe how the hub sits in your build and Pybricks reports
the heading in robot coordinates for you. Get them wrong and every turn is
wrong, so check them first after a rebuild.

The take-your-hands-off delay and the stop button live in **`constants.py`**,
commented inline.

### Measuring the robot

Run **`check_directions.py`** first: if the robot spins on the spot or drives
backwards, flip a wheel direction in `config.py`.

Then **`drivebase_test.py`** measures the two numbers every run depends on.
Upload it with everything else and run it instead of `main.py`; results print
in the Pybricks Code terminal on lines starting `5.1`.

| Letter | What to do | What it gives you |
|---|---|---|
| **B** | Run it three times; measure how far it really went each time | `WHEEL_DIAMETER_MM` = current value x average mm / 1000 |
| **C** | Run it twice | the `AXLE_TRACK_MM` it suggests |

Measure B to the same point on the robot every time -- the front edge of one
wheel, say. A turn depends on axle track / wheel diameter, so **whenever the
wheel number changes, scale the axle track by the same ratio** before running
C again. Settled is when C reads within a few degrees of 360.

Put the same two numbers in the planner's robot profile. The hub always drives
with `config.py`'s -- a run's distances are real millimetres on the field, so
what matters is *this* robot's own measurements -- and if a run was planned
with different ones, it prints a warning saying so and drives anyway.

The other letters (A, D-F, H-J) are the checks that showed this approach
works on the hub, kept for re-checking after a firmware update or a rebuild.

## Running

`main.py` is what you run on the hub. It is deliberately tiny:

```python
from runs import selector

selector.run_forever()
```

Everything you actually write goes in **`runs.py`**.

### Selecting runs

The hub only has `LEFT`, `RIGHT` and `CENTER`, so the EV3's one-run-per-button
scheme is gone. Instead the display shows a **letter**:

| Button | What it does |
|---|---|
| **CENTER** | run the letter currently shown |
| **RIGHT** | jog to the next letter, without running it |
| **LEFT** | jog back a letter, without running it |
| **BLUETOOTH** | **stop the program** |

> **The stop button has moved.** Pybricks normally stops a running program
> when you press CENTER -- which would kill this one the instant you tried to
> start a run. `Robot` therefore reassigns the stop button to **BLUETOOTH** at
> startup. That is now your abort button, and it matters: while a run is
> going, the robot is driving.
>
> Change it with `STOP_BUTTON` in `constants.py`. Setting it to `None` frees
> that button too, but then the only way out is holding CENTER for three
> seconds, which powers the hub off.

When a run finishes, the selector **advances to the next letter by itself**.
So in a match where nothing goes wrong, the technician only ever taps CENTER.
`LEFT`/`RIGHT` are there for when something does: skip a run, or go back and
repeat one.

This is Pybricks' own `hub_menu()` idea, minus the part where you have to
re-select every single time.

### Adding a run from the planner

Plan the run in the web planner and press **Download .py**. Put the file next
to the others (name it something Python can import, like `run_b.py`), then
wire it into `runs.py`:

```python
import run_b as planned_b      # NOT `import run_b` -- see below

def run_b():
    planned_b.run(core)

selector = RunSelector(
    core,
    runs=[run_a, run_b],       # first is A, second is B, ...
    before=start_run,          # optional, runs before every run
    after=stop_run,            # optional, runs after every run
    wrap=True,                 # cycle back to A after the last run
    one_time_use=False,        # True: a letter disappears once it has run
)
```

> **Import it under another name.** `import run_b` next to `def run_b()` is the
> same name twice in one file, and the function silently replaces the module --
> so `run_b.run(core)` would call the function, not the run.

`RunSelector` also takes `labels=['X', 'Y', 'Z']` if you would rather not use
A, B, C.

### What a run file looks like

A downloaded run is short enough to read, and worth reading:

```python
"""run_a, generated by PythFinder -- do not edit."""

from pybricks.parameters import Stop
from pybricks.tools import wait


def _action_1(core):
    """arm down"""
    if core.leftTask is not None:
        core.leftTask.run(500)


def run(core):
    """Drive this run. The only thing runs.py needs to call."""
    # Team robot
    drive = core.configure(
        wheel_diameter=55.6, axle_track=160.1,
        straight_speed=200, straight_acceleration=400,
        turn_rate=150, turn_acceleration=300,
        use_gyro=True)
    core.set_heading(0)

    drive.straight(350, then=Stop.NONE)
    _action_1(core)        # arm down
    drive.straight(400)
    wait(600)
    core.turn_to(90, 90)
    ...

    core.stopTaskMotors()
```

- **`drive.straight(mm)`** and the turns are Pybricks' `DriveBase`: the motion
  runs in the hub's firmware, holding the distance on the wheel encoders and
  the heading on the gyro.
- **`then=Stop.NONE`** keeps rolling into the next straight without slowing
  down. That is how an action fires partway through a drive: the drive is
  split there, and the action runs in between.
- **`core.turn_to(heading, by)`** turns to face a heading on the field (0 is up
  the field, 90 to the right), working from where the gyro says the robot
  really is -- so a drift on one drive is corrected at the next turn instead
  of carried forward. `by` is how far, and which way, the plan turned: it
  matters when a turn was planned the long way round, to sweep a different
  part of the mat.
- **`core.configure(...)`** applies the run's speeds; the wheel and axle track
  stay `config.py`'s (see [Measuring the robot](#measuring-the-robot)).
- **Actions** while driving must return at once -- start a motor, do not wait
  for it. An arm step on its own does wait (`wait=True`), and the robot stands
  still until it is done.

## Tools

Run any of these instead of `main.py`:

| File | What it is for |
|---|---|
| `drivebase_test.py` | measure wheel diameter and axle track; re-check DriveBase after a rebuild |
| `check_directions.py` | check each wheel turns the right way |
| `check_wheel_balance.py` | robot veers? hold it in the air to tell a weak motor from a dragging wheel |
| `measure_max_velocity.py` | the robot's top speed, for the planner's robot profile |

## TeleOp

`teleop.py` drives the robot from a game controller so you can test
attachments without writing a run. Run that file instead of `main.py`.

Pybricks only speaks to **Xbox controllers** -- the EV3 version's PS3/PS4
support read raw Linux input events and has no equivalent on the hub.

| Control | Action |
|---|---|
| **X** | select the LEFT task motor |
| **B** | select the RIGHT task motor |
| **left stick, Y** | drive forwards / backwards |
| **right stick, X** | turn |
| **D-pad up** | run the selected task motor forwards |
| **D-pad down** | run the selected task motor backwards |
| **D-pad left** | stop the selected task motor |

<br/>

# What changed from the EV3 version

The EV3 runs Pybricks on top of ev3dev Linux. The hub runs bare-metal
MicroPython. That difference drives most of this:

| | EV3 | SPIKE Prime |
|---|---|---|
| Runs | a `.txt` of wheel powers, played back against the clock | a `.py` of `DriveBase` calls from the web planner |
| Distance | open loop -- powers assumed to cover the ground | closed loop on the wheel encoders |
| Heading | external gyro, heading PID in Python | the hub's built-in IMU, DriveBase's own control |
| Config | `hardware.cfg` INI file | `config.py` |
| Markers | one thread each | the drive is split, and the action runs between |
| Run selection | one run per direction button | letter + CENTER, auto-advancing |
| Stop button | dedicated back button | CENTER by default, moved to BLUETOOTH |
| Screen | 178x128 text | 5x5 LED matrix, one character |
| Layout | packages in folders | flat files, no subdirectories |
| TeleOp | PS3/PS4 via `/dev/input` | Xbox via `pybricks.iodevices` |
| Ports | `A`-`D` motors, `S1`-`S4` sensors | `A`-`F` for everything |

This branch first ported the EV3's recorded format as it was -- wheel powers
played back by a follow loop with a heading PID -- and then replaced it. The
recorded data cost about 6 bytes per 6 ms of driving on a small heap, and the
follow loop corrected heading but never checked distance, so battery level
and wheel slip went straight into where the robot ended up. The DriveBase
version measured repeatable on the robot and is a fraction of the size.
PythFinder's `docs/web-planner.md` (phase 5) has the whole story, with the
measurements.

Carried over unchanged: `math_ex.py` and `edge_detector.py`.

## Advanced usage

*Check out the full library [here][1].*

*v. 0.0.4-alpha*

[0]: https://pybricks.com/learn/getting-started/install-pybricks/ "install pybricks"
[1]: https://github.com/omegacoreFLL/PythFinder
[2]: https://code.pybricks.com
