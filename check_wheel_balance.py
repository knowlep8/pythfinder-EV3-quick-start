"""
Find out WHY the robot veers, by timing each drive wheel on its own.

measure_max_velocity.py drives both wheels at one duty cycle with no gyro
correction, so any difference between the sides shows up as a curve. That tells
you the robot veers, but not why. There are two quite different causes and they
need opposite fixes:

    the motor is weaker   -- one side genuinely turns slower for the same duty
                             cycle, even with nothing to push against
    the wheel is loaded   -- both motors are fine, but one side drags on an
                             axle, a beam, or a tight bushing; or the two
                             wheels are not the same size

Run this with the ROBOT HELD IN THE AIR. With nothing to push against, drag and
wheel size drop out of the picture, so whatever difference is left is the
motors. Compare that against the `imbalance` measure_max_velocity.py prints,
which is the same two sides measured under load:

    differ in the air AND on the ground  -- the motor
    match in the air, differ on ground   -- drag, grip, or a mismatched wheel

It also finds each side's breakaway duty: the lowest power that gets the wheel
moving at all. PythFinder assumes power is proportional to velocity straight
through zero, so everything below breakaway is commanded but never driven --
which is what eats the ramps at both ends of every straight.

Upload alongside the other files at code.pybricks.com and run this file
instead of main.py.
"""

# Pybricks calls it umath, and has no `math` under that name -- see math_ex.py
try:
    import umath as math
except ImportError:
    import math

from pybricks.tools import StopWatch, wait

from math_ex import clipMotor
# Imported rather than repeated: these two files disagreeing about the wheel is
# exactly the sort of thing that makes a run come out the wrong length.
from measure_max_velocity import GEAR_RATIO, WHEEL_DIAMETER_CM, wait_for_center
from robot import Robot


# Duty levels to compare the sides at. The low ones matter most: that is where
# a trajectory spends its ramps, and where a weak side shows up first.
DUTY_LEVELS = (20, 30, 40, 60, 80, 100)

SPIN_MS = 1000
SETTLE_MS = 300
REST_MS = 250

# Breakaway search: creep the duty up until the wheel actually moves.
BREAKAWAY_HOLD_MS = 150
BREAKAWAY_MOVED_DEG = 10
BREAKAWAY_MAX = 60

# Below this, motor-to-motor variation is normal and not worth chasing.
MATCHED_PERCENT = 5


def _cm(degrees):
    return degrees / 360.0 * GEAR_RATIO * math.pi * WHEEL_DIAMETER_CM


def _drive(robot, motor, power):
    """One side, through exactly the arithmetic setWheelPowers() uses.

    Going through normalizeVoltage() and clipMotor() rather than motor.dc()
    directly keeps these numbers in the same units the planner emits, so a
    breakaway figure read here can be compared against a power in DATA.
    """
    motor.dc(clipMotor(robot.normalizeVoltage(power)))


def free_speed(robot, motor, duty):
    """Degrees per second this motor reaches at a given duty cycle."""
    motor.reset_angle(0)
    _drive(robot, motor, duty)

    # let it reach a steady speed before the clock starts
    wait(SETTLE_MS)

    start = motor.angle()
    timer = StopWatch()
    wait(SPIN_MS)
    elapsed = timer.time()
    moved = motor.angle() - start

    motor.brake()
    wait(REST_MS)

    return moved / (elapsed / 1000.0)


def breakaway(robot, motor):
    """Lowest duty cycle that gets this wheel turning at all."""
    for duty in range(1, BREAKAWAY_MAX + 1):
        motor.reset_angle(0)
        _drive(robot, motor, duty)
        wait(BREAKAWAY_HOLD_MS)
        moved = abs(motor.angle())

        motor.brake()
        wait(REST_MS)

        if moved >= BREAKAWAY_MOVED_DEG:
            return duty

    return None


def main():
    core = Robot()
    hub = core.hub

    print("\nWHEEL BALANCE")
    print("battery {0:.2f}V".format(core.voltage))
    print("wheel   {0} cm".format(WHEEL_DIAMETER_CM))
    print("\nHOLD THE ROBOT IN THE AIR, so both wheels spin free.")
    print("press CENTER when you have it")
    wait_for_center(hub)

    print("\n duty      left     right      diff")

    # signed, so the verdict below can name a side: positive means the right
    # wheel ran faster, and therefore that the LEFT one is the weak side
    worst = 0.0
    fastest = None

    for duty in DUTY_LEVELS:
        hub.display.char("L")
        left = free_speed(core, core.leftDrive, duty)

        hub.display.char("R")
        right = free_speed(core, core.rightDrive, duty)

        mean = (left + right) / 2.0
        diff = (right - left) / mean * 100.0 if mean else 0.0

        if abs(diff) > abs(worst):
            worst = diff

        if duty == 100:
            fastest = (left, right)

        print("{0:4d}%   {1:7.1f}   {2:7.1f}   {3:+6.1f}%   deg/s".format(
            duty, left, right, diff))

    if fastest is not None:
        print("\nat full power that is {0:.1f} cm/s left, {1:.1f} cm/s right,"
              .format(_cm(fastest[0]), _cm(fastest[1])))
        print("unloaded -- expect the real number on the ground to be lower")

    hub.display.char("B")
    print("\nbreakaway -- lowest duty that moves the wheel at all")
    left_break = breakaway(core, core.leftDrive)
    right_break = breakaway(core, core.rightDrive)

    print("  left   {0}".format(
        "{0}%".format(left_break) if left_break else "did not move"))
    print("  right  {0}".format(
        "{0}%".format(right_break) if right_break else "did not move"))

    print("\n----------------------------------------")

    if abs(worst) < MATCHED_PERCENT:
        print("the motors MATCH in the air ({0:.1f}% worst case)."
              .format(abs(worst)))
        print("so the veer is not the motors. Look for:")
        print("  - two different wheels, or one not pushed fully onto the axle")
        print("  - an axle rubbing a beam, or a bushing that is too tight")
        print("  - weight sitting off to one side")
        print("  - one wheel slipping, if the mat has a slick patch")
    else:
        print("the {0} motor is weaker by {1:.1f}% IN THE AIR."
              .format("left" if worst > 0 else "right", abs(worst)))
        print("that is the motor itself, not the build. Try swapping the two")
        print("drive motors between ports: if the veer swaps sides with them,")
        print("it is the motor; if it stays put, it is the build after all.")

    print("\nbreakaway is what PythFinder does not model: it assumes power is")
    print("proportional to speed straight through zero. Every ramp spends its")
    print("first moments below these numbers, commanded but not moving.")

    hub.display.char("K")


if __name__ == "__main__":
    main()
