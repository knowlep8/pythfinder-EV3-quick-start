<p align="center" style="margin-bottom: 10px;">
      <img src="https://i.ibb.co/mHSpjdL/pyth-finder-logo-ev3-quickstart.png" alt="pyth-finder-logo" border="0">
</p>

![version_badge](https://img.shields.io/badge/alpha-0.0.4-006400)
![quickstart](https://img.shields.io/badge/SPIKE_Prime_implementation-006400)
![license](https://img.shields.io/badge/license-MIT-62e39e)

A [PythFinder][1] trajectory runner for the **LEGO SPIKE Prime / Robot Inventor
hub**, running [Pybricks][0].

> Looking for the EV3 version? It lives on the `main` branch. This branch is a
> port, not a superset: the hub has no filesystem, no threading, and only three
> usable buttons, so several things work differently. See
> [What changed from the EV3 version](#what-changed-from-the-ev3-version).

# Installation

## Pybricks

Install the Pybricks firmware on your hub by following the
[**official guide**][0]. Everything here runs in the browser at
[code.pybricks.com][2] -- there is no VS Code extension for Pybricks, so the
usual workflow is to edit these files locally and paste or upload them there.

You do **not** need to install anything with pip to run the robot. The only
thing that runs on your computer is `tools/txt_to_py.py`, which needs plain
Python 3 and no dependencies.

## This project

Clone the repo and check out this branch:

```bash
git clone https://github.com/omegacoreFLL/pythfinder-EV3-quick-start.git
cd pythfinder-EV3-quick-start
git checkout spike-port
```

In [code.pybricks.com][2], create a project and add each `.py` file from the
repository root. Pybricks bundles any module you `import` along with your main
program, so all of them travel to the hub together.

> **Files must sit flat, side by side.** Pybricks does not support
> subdirectories, which is why this branch has no `BetterClasses/`,
> `Controllers/` or `Settings/` folders. `Trajectory/` and `tools/` stay on
> your computer and are never uploaded.

<br/>

# Usage

## Setup

Open **`config.py`** and describe your robot. This is the only file you have to
touch to get moving:

```python
# how the hub is mounted
HUB_TOP_SIDE = Axis.Z
HUB_FRONT_SIDE = Axis.X

# motors -- the hub has six identical ports, A through F
LEFT_WHEEL_PORT = Port.A
RIGHT_WHEEL_PORT = Port.B
LEFT_TASK_PORT = Port.C
RIGHT_TASK_PORT = Port.D

# sensors go in those same A-F ports
COLOR_SENSOR_LEFT_PORT = Port.E
COLOR_SENSOR_RIGHT_PORT = Port.F
ATTACHMENT_COLOR_SENSOR_PORT = None

# flip one of these if a wheel spins backwards
LEFT_WHEEL_DIRECTION = Direction.CLOCKWISE
RIGHT_WHEEL_DIRECTION = Direction.CLOCKWISE
```

**Two wheel motors are required.** Task motors and color sensors are optional --
set a port to `None` if you do not have that part.

`HUB_TOP_SIDE` / `HUB_FRONT_SIDE` replace the EV3's external gyro and its four
orientation flags. Describe how the hub sits in your build and Pybricks reports
the heading in robot coordinates for you.

Finer tuning -- PID gains, the take-your-hands-off delay, the battery
reference -- lives in **`constants.py`**, commented inline.

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

When a run finishes, the selector **advances to the next letter by itself**.
So in a match where nothing goes wrong, the technician only ever taps CENTER.
`LEFT`/`RIGHT` are there for when something does: skip a run, or go back and
repeat one.

This is Pybricks' own `hub_menu()` idea, minus the part where you have to
re-select every single time.

### Writing runs

```python
core = Robot()
trajectory1 = Trajectory(traj_test)

def run_a():
    trajectory1.follow(core)

def run_b():
    trajectory20.follow(core)
    wait(500)
    trajectory21.follow(core)

selector = RunSelector(
    core,
    runs=[run_a, run_b],       # first is A, second is B, ...
    before=start_run,          # optional, runs before every run
    after=stop_run,            # optional, runs after every run
    wrap=True,                 # cycle back to A after the last run
    one_time_use=False,        # True: a letter disappears once it has run
)
```

`RunSelector` also takes `labels=['X', 'Y', 'Z']` if you would rather not use
A, B, C.

## Trajectories

The hub has no filesystem, so a trajectory can no longer be read from a `.txt`
at runtime. Convert it on your computer first:

```bash
python3 tools/txt_to_py.py Trajectory/TXT/mypath.txt
```

That writes `traj_mypath.py`, which you upload alongside everything else:

```python
import traj_mypath

trajectory1 = Trajectory(traj_mypath)
```

Then follow it with `.follow(core)`.

The generated module stores the path as one compact `bytes` constant rather
than a list of numbers, because the hub's heap is small. The bundled
`traj_test` is 1965 states over 11.8 seconds and costs about **11.8 kB**.

### Markers

If your path has markers, bind a function to each one in path order:

```python
trajectory1 = (Trajectory(traj_mypath)
               .withMarkers((drop_arm, raise_arm)))
```

> **Markers run inline.** The EV3 fired each marker on its own thread; the hub
> has no `threading` module, so a marker now runs *on the follow loop*. Keep
> marker functions short and non-blocking -- anything slow will stall the path
> being followed.

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
MicroPython. That difference drives nearly all of this:

| | EV3 | SPIKE Prime |
|---|---|---|
| Trajectory data | `open()` a `.txt` at runtime | generated `.py` module, converted on the PC |
| Config | `hardware.cfg` INI file | `config.py` |
| Markers | one thread each | run inline on the follow loop |
| Heading | external gyro sensor | the hub's built-in IMU |
| Run selection | one run per direction button | letter + CENTER, auto-advancing |
| Screen | 178x128 text | 5x5 LED matrix, one character |
| Layout | packages in folders | flat files, no subdirectories |
| TeleOp | PS3/PS4 via `/dev/input` | Xbox via `pybricks.iodevices` |
| Ports | `A`-`D` motors, `S1`-`S4` sensors | `A`-`F` for everything |

Carried over unchanged: `math_ex.py`, `edge_detector.py`, `pid.py`, the
run-length-encoded trajectory format, and the feed-forward + heading-PID
follow loop that made the EV3 version fast.

## Advanced usage

*Check out the full library [here][1].*

*v. 0.0.4-alpha*

[0]: https://pybricks.com/learn/getting-started/install-pybricks/ "install pybricks"
[1]: https://github.com/omegacoreFLL/PythFinder
[2]: https://code.pybricks.com
