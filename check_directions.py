"""
Work out which wheel is wired backwards.

If the robot spins on the spot when both wheels are given the same positive
power, one of them is turning the wrong way. This drives them one at a time so
you can see which.

Run this instead of main.py. Hold the robot in the air, or give it room -- it
only moves in short bursts, but it does move.

What you should see, for each wheel in turn:

    that wheel rolls FORWARD (the direction the robot's front points)

If a wheel rolls backward, flip that side's direction in config.py:

    Direction.CLOCKWISE  <->  Direction.COUNTERCLOCKWISE

The two sides normally need OPPOSITE values, because the motors are mounted
mirrored: "clockwise" is measured at each motor's own shaft, and those shafts
point opposite ways.
"""

from pybricks.parameters import Button, Stop
from pybricks.tools import wait

import config
from robot import Robot


BURST_MS = 1200
POWER = 40


def wait_for_center(hub):
    while Button.CENTER in hub.buttons.pressed():
        wait(20)
    while Button.CENTER not in hub.buttons.pressed():
        wait(20)
    while Button.CENTER in hub.buttons.pressed():
        wait(20)


def jog(hub, motor, name, direction):
    hub.display.char(name[0])
    print("\n{0} wheel, configured {1}".format(name, direction))
    print("  press CENTER -- watch which way it rolls")
    wait_for_center(hub)

    motor.dc(POWER)
    wait(BURST_MS)
    motor.brake()

    print("  did it roll FORWARD? if not, flip {0}_WHEEL_DIRECTION"
          .format(name.upper()))


def main():
    core = Robot()
    hub = core.hub

    print("\nWHEEL DIRECTION CHECK")
    print("left  is on {0}, configured {1}".format(
        config.LEFT_WHEEL_PORT, config.LEFT_WHEEL_DIRECTION))
    print("right is on {0}, configured {1}".format(
        config.RIGHT_WHEEL_PORT, config.RIGHT_WHEEL_DIRECTION))

    if config.LEFT_WHEEL_DIRECTION is config.RIGHT_WHEEL_DIRECTION:
        print("\nboth sides are set to the same Direction. On a normally")
        print("mirrored drivetrain that makes one wheel drive backwards,")
        print("which is exactly what spinning on the spot looks like.")

    jog(hub, core.leftDrive, "left", config.LEFT_WHEEL_DIRECTION)
    jog(hub, core.rightDrive, "right", config.RIGHT_WHEEL_DIRECTION)

    print("\nboth together -- this should drive straight forward")
    print("  press CENTER")
    wait_for_center(hub)

    core.setWheelPowers(POWER, POWER)
    wait(BURST_MS)
    core.setDriveTo(Stop.BRAKE)

    hub.display.char("K")


if __name__ == "__main__":
    main()
