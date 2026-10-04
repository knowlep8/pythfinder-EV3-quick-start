"""
Measure the robot's real top speed, for PythFinder's real_max_velocity.

PythFinder turns a planned speed into a motor power with

    power = speed * MAX_POWER / REAL_MAX_VEL

so REAL_MAX_VEL has to be the speed this robot actually reaches at full power.
If it is wrong, every straight in every run comes out the wrong length. The
value shipped with the library is 27.7 cm/s, measured on somebody else's EV3.

This drives through Robot.setWheelPowers() rather than talking to the motors
directly, so the number you get includes the same battery-voltage compensation
your real runs use.

    YOU NEED ABOUT 1.5 METRES OF CLEAR RUNWAY. Point the robot down the long
    side of the mat, or use the floor. It stops itself, but it does not look
    where it is going.

Upload alongside the other files at code.pybricks.com and run this file
instead of main.py. Press CENTER to start each attempt; the result prints to
the console when all of them are done.
"""

# Pybricks calls it umath, and has no `math` under that name -- see math_ex.py
try:
    import umath as math
except ImportError:
    import math

from pybricks.parameters import Button, Stop
from pybricks.tools import StopWatch, wait

from robot import Robot


# --- your build -------------------------------------------------------------

# Measured on the rebuilt base with drivebase_test.py -- config.py's
# WHEEL_DIAMETER_MM, in cm.
WHEEL_DIAMETER_CM = 5.56

# Wheel turns per motor turn. 1 means the wheel is on the motor shaft. If you
# geared it, put the ratio here or the distance will be wrong.
GEAR_RATIO = 1.0


# --- how the measurement is taken -------------------------------------------

# Ignore the first stretch so the robot is at a steady speed before timing.
SETTLE_MS = 600

# The timed window. Longer is more accurate but needs more runway.
MEASURE_MS = 1200

# How long to let the robot coast to a standstill after braking, so the
# encoders can be read once it has genuinely stopped.
STOP_MS = 800

ATTEMPTS = 3


def _cm(degrees):
    return degrees / 360.0 * GEAR_RATIO * math.pi * WHEEL_DIAMETER_CM


def _wheels_cm(robot):
    """How far each wheel has rolled since the encoders were zeroed."""
    return _cm(robot.leftDrive.angle()), _cm(robot.rightDrive.angle())


def _centre(robot):
    """A differential drive's centre travels the mean of its two wheels,
    whether it went straight or curved."""
    left, right = _wheels_cm(robot)
    return (left + right) / 2.0


def attempt(robot):
    robot.leftDrive.reset_angle(0)
    robot.rightDrive.reset_angle(0)

    robot.setWheelPowers(100, 100)

    # the run-up is spent accelerating, so it is deliberately not timed
    wait(SETTLE_MS)
    run_up = _centre(robot)

    left_start, right_start = _wheels_cm(robot)
    timer = StopWatch()
    wait(MEASURE_MS)
    elapsed_ms = timer.time()
    left_end, right_end = _wheels_cm(robot)

    robot.setDriveTo(Stop.BRAKE)
    end_of_power = _centre(robot)

    # braking covers real ground, and a tape measure sees it. Wait for the
    # robot to actually stop before reading, or the totals will not match
    # anything you can measure on the floor.
    wait(STOP_MS)
    total = _centre(robot)

    return (left_end - left_start, right_end - right_start, elapsed_ms,
            run_up, total - end_of_power, total)


def wait_for_center(hub):
    while Button.CENTER in hub.buttons.pressed():
        wait(20)
    while Button.CENTER not in hub.buttons.pressed():
        wait(20)
    while Button.CENTER in hub.buttons.pressed():
        wait(20)


def main():
    core = Robot()
    hub = core.hub

    print("\nMAX VELOCITY")
    print("battery {0:.2f}V".format(core.voltage))
    print("clear about 1.5m ahead of the robot")

    print("this drives raw power with NO gyro correction, so some curve is")
    print("normal -- Trajectory.follow() is what straightens a real run")

    speeds = []
    imbalances = []

    for i in range(ATTEMPTS):
        hub.display.char(str(i + 1))
        print("\nattempt {0} of {1} -- press CENTER".format(i + 1, ATTEMPTS))
        wait_for_center(hub)

        left, right, elapsed_ms, run_up, braking, total = attempt(core)
        centre = (left + right) / 2.0
        speed = centre / (elapsed_ms / 1000.0)

        speeds.append(speed)
        if centre:
            imbalances.append((right - left) / centre * 100.0)

        # three separate stretches of one run: only the middle one is timed,
        # and all three together are what a tape measure sees
        print("  run-up   {0:6.1f} cm   speeding up, not timed".format(run_up))
        print("  TIMED    {0:6.1f} cm   in {1} ms   (left {2:.1f}, right {3:.1f})"
              .format(centre, elapsed_ms, left, right))
        print("  braking  {0:6.1f} cm".format(braking))
        print("  total    {0:6.1f} cm   start to standstill".format(total))
        print("  speed    {0:6.1f} cm/s".format(speed))

    average = sum(speeds) / len(speeds)
    spread = max(speeds) - min(speeds)
    imbalance = sum(imbalances) / len(imbalances) if imbalances else 0.0

    print("\n----------------------------------------")
    print("average    {0:.1f} cm/s".format(average))
    print("spread     {0:.1f} cm/s".format(spread))
    print("imbalance  {0:+.1f}%  ({1} wheel is faster)".format(
        imbalance, "right" if imbalance > 0 else "left"))

    if spread > average * 0.1:
        print("\nthose attempts disagree by more than 10%. Usually that means")
        print("the robot was still speeding up, or a wheel slipped. Try a")
        print("longer MEASURE_MS, or a surface with more grip.")

    if abs(imbalance) > 8:
        print("\n{0:.0f}% is more than motor-to-motor variation.".format(
            abs(imbalance)))
        print("Check for a rubbing wheel, a tight axle, uneven weight, or two")
        print("different motor types on the drive. The heading PID can hide")
        print("this, but it spends its correction range doing so.")

    print("\nput this in PythFinder, constants.py:")
    print("    fll_real_max_velocity = {0:.1f}".format(average))
    print("\nThe three stretches above are parts of one run: the robot speeds")
    print("up, then holds speed for the TIMED window, then brakes. Only the")
    print("middle one sets the speed; all three add up to 'total'.")
    print("\nTape-measure 'total' -- start line to where it stops. If the robot")
    print("moved less than the wheels claim, it is slipping and the real speed")
    print("is lower than this.")

    hub.display.char("K")


if __name__ == "__main__":
    main()
