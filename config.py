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
LEFT_WHEEL_PORT = Port.F
RIGHT_WHEEL_PORT = Port.B

LEFT_TASK_PORT = Port.C
RIGHT_TASK_PORT = Port.D


# --- sensors ----------------------------------------------------------------
COLOR_SENSOR_LEFT_PORT = Port.E
COLOR_SENSOR_RIGHT_PORT = Port.A

# A third color sensor used to auto-identify the mounted attachment.
ATTACHMENT_COLOR_SENSOR_PORT = None


# --- directions -------------------------------------------------------------
# Which way a positive power turns each motor. Flip one of these if a wheel
# spins backwards.
LEFT_WHEEL_DIRECTION = Direction.CLOCKWISE
RIGHT_WHEEL_DIRECTION = Direction.CLOCKWISE

LEFT_TASK_DIRECTION = Direction.COUNTERCLOCKWISE
RIGHT_TASK_DIRECTION = Direction.COUNTERCLOCKWISE


# --- derived ----------------------------------------------------------------
# Same rule the EV3 ConfigReader enforced: both wheel motors are mounted
# mirrored, so they take the same Direction. If they disagree, something is
# wrong with the config rather than with the robot.
if LEFT_WHEEL_DIRECTION is not RIGHT_WHEEL_DIRECTION:
    print("\n\nWheel motor directions should match, but LEFT is {0} and RIGHT is {1}"
          .format(LEFT_WHEEL_DIRECTION, RIGHT_WHEEL_DIRECTION))
    print("Using {0} for both. If you meant this, edit config.py."
          .format(LEFT_WHEEL_DIRECTION))
    RIGHT_WHEEL_DIRECTION = LEFT_WHEEL_DIRECTION

# Sign of the heading correction, so a mirrored drivetrain still steers the
# right way. Consumed by Trajectory.follow().
PID_MULTIPLIER = 1 if LEFT_WHEEL_DIRECTION is Direction.CLOCKWISE else -1
