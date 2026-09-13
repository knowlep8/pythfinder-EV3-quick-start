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
LEFT_WHEEL_PORT = Port.E
RIGHT_WHEEL_PORT = Port.A

LEFT_TASK_PORT = Port.B
RIGHT_TASK_PORT = Port.F


# --- sensors ----------------------------------------------------------------
COLOR_SENSOR_LEFT_PORT = Port.C
COLOR_SENSOR_RIGHT_PORT = Port.D

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
