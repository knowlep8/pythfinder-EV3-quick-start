"""
Hardware configuration -- this is the file you edit for YOUR robot.

Replaces the EV3's Settings/hardware.cfg + ConfigReader.py. The hub has no
filesystem, so an .ini file can no longer be read at runtime; the values live
here as plain Python instead.

Two wheel motors are required. Everything else is optional -- set it to None
if your robot does not have it.
"""

from pybricks.parameters import Axis, Direction, Port


# --- how the hub is mounted -------------------------------------------------
# Which way the hub faces in your build. The hub's IMU replaces the EV3's
# external gyro, so instead of the old up_side_down / front_side_back flags you
# just describe the orientation and Pybricks does the rest.
#
#   TOP_SIDE   -- the axis pointing out of the hub's top face (the buttons)
#   FRONT_SIDE -- the axis pointing to the front of the robot
#
# Defaults match a hub sitting flat, ports A/B on the left, USB to the back.
HUB_TOP_SIDE = Axis.Z
HUB_FRONT_SIDE = Axis.X


# --- motors -----------------------------------------------------------------
# The Prime hub has six identical ports, A through F. Unlike the EV3 there is
# no separate set of sensor ports -- sensors go in the same A-F ports.
# Rebuilt base, 2026-09-27: the wheels moved from C/D to F/B.
LEFT_WHEEL_PORT = Port.F
RIGHT_WHEEL_PORT = Port.B

LEFT_TASK_PORT = Port.A
RIGHT_TASK_PORT = Port.E


# --- sensors ----------------------------------------------------------------
# The rebuilt base has no colour sensors (they were on B and F, which the
# wheels now use).
COLOR_SENSOR_LEFT_PORT = None
COLOR_SENSOR_RIGHT_PORT = None

# A third color sensor used to auto-identify the mounted attachment.
ATTACHMENT_COLOR_SENSOR_PORT = None


# --- directions -------------------------------------------------------------
# Which way a positive power turns each motor. Flip one of these if a wheel
# spins backwards.
#
# The two sides normally need OPPOSITE values. "Clockwise" is measured at each
# motor's own output shaft, and on a mirrored drivetrain those shafts point
# opposite ways -- so giving both sides the same Direction drives one wheel
# forward and the other backward, and the robot spins on the spot.
LEFT_WHEEL_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_WHEEL_DIRECTION = Direction.CLOCKWISE

LEFT_TASK_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_TASK_DIRECTION = Direction.COUNTERCLOCKWISE


# --- driving with DriveBase ---------------------------------------------------
# What core.drive_base starts as. A file from the web planner passes its own
# robot profile's numbers to core.configure() and these are only the fallback
# for a run without one -- but they are what drivebase_test.py measures, so
# keep them up to date.
#
# A turn depends on axle track / wheel diameter, so when the wheel number
# changes, scale the axle track with it.
#
# Rebuilt base, 2026-09-27. Wheel: B three times at 54.6 (the old base's)
# went 40 1/4, 40, 40 in -- mean 1018 mm -- so 54.6 x 1.018. Axle track: C at
# 55.6 / 168.8 (the old base's number, scaled) turned 379.6 for 360, so
# 168.8 x 360 / 379.6 -- this base is narrower than the old one. Checked by
# a second C at 55.6 / 160.1: 360.2 for 360.
WHEEL_DIAMETER_MM = 55.6
AXLE_TRACK_MM = 160.1


# --- derived ----------------------------------------------------------------
# Sign of the heading correction, consumed by Trajectory.follow().
#
# This used to be derived from LEFT_WHEEL_DIRECTION, which only made sense
# while both sides were forced to share a Direction. Now that they differ --
# as they must on a mirrored drivetrain -- neither side's Direction says
# anything about which way the robot steers, so it is set explicitly.
#
# 1 is right whenever positive power drives both wheels forward. If a
# trajectory veers off its line harder and harder instead of settling onto it,
# the correction is fighting the robot: set this to -1.
PID_MULTIPLIER = 1
