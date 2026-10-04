"""
DriveBase checks -- step 5.1 of PythFinder's docs/web-planner.md.

A THROWAWAY program: run this file from Pybricks Code instead of main.py. It
answers the questions phase 5 depends on before anything is built:

    A  firmware       version, and whether this firmware has what phase 5 uses
    B  wheel size     drives 1000 mm -- measure how far it really went
    C  axle track     turns 360 on the wheels alone, reads the gyro
    D  the join       is straight(then=NONE) + straight() seamless?
    E  settings       does settings() work while the robot is still rolling?
    F  after a nudge  is turn() relative to the real heading, or the old target?
    H  new square     run_square's square with DriveBase, turning BY 90 each time
    I  new square     the same, turning TO each heading off the gyro
    J  other wheel    a run planned with a different wheel still drives

The letters work like main.py: the display shows one, CENTER runs it, LEFT and
RIGHT move between them. Everything worth writing down is printed in the
Pybricks Code terminal on lines starting "5.1", so keep the hub connected.

There is no G any more: it drove the square with the old follow loop, which
has been removed. The letters after it keep their names so the results
recorded in docs/web-planner.md still match.

For H and I, mark where the robot starts, and after each run measure how
far the front of the robot ended up from where it should be. Do each one five
times, once on a full battery and once on a tired one (the voltage is printed).
"""

from pybricks import version
from pybricks.parameters import Stop
from pybricks.tools import StopWatch, wait

import config
from robot import Robot
from run_selector import RunSelector


# --- the numbers under test ---------------------------------------------------
# These now live in config.py, where robot.py builds core.drive_base from
# them -- B and C measure config.py's numbers, so correct them THERE.
#
# On the old base (before the rebuild), 2026-09-27: B at 56 first read 38 in,
# a mis-measurement; at 54.1 three careful runs went 39 1/2, 39 3/4 and 40 in
# (mean 1010 mm), giving 54.6. C, twice at 54.1 / 162.9, read 359.1 and 354.8
# (mean suggestion 164.3), scaled by 54.6 / 54.1 to 165.8. A turn depends on
# axle track / wheel diameter, so when the wheel changes, scale the axle too.
WHEEL_DIAMETER_MM = config.WHEEL_DIAMETER_MM
AXLE_TRACK_MM = config.AXLE_TRACK_MM

# run_square's plan: drive this many mm,
# then turn to face this heading. 0 is up the field, 90 is to the right.
SQUARE = ((400, 90), (300, 180), (300, 270), (300, 0))

# The old recorded run's cruise: 43.08% power x 64.3 cm/s top speed, kept so
# H and I drive at the pace the follow loop did when they were compared.
SQUARE_SPEED = 277


core = Robot()

# robot.py's own DriveBase, rather than a second one on the same motors --
# whether Pybricks allows two at once is not known yet
drive_base = core.configure()

# (straight_speed, straight_acceleration, turn_rate, turn_acceleration),
# as the firmware picked them for this wheel size, so each test starts clean
DEFAULTS = drive_base.settings()

timer = StopWatch()


def report(test, text):
    print("5.1 {0}: {1}".format(test, text))


def voltage():
    return core.hub.battery.voltage() / 1000


def heading():
    # raw, so it does not wrap -- a 360 turn reads 360, not 0
    return core.hub.imu.heading()


def fresh(use_gyro=True):
    """Stopped, zeroed and at default speeds -- run before every test."""
    drive_base.stop()
    drive_base.settings(*DEFAULTS)

    try:
        drive_base.use_gyro(use_gyro)
    except AttributeError:
        pass            # test A says so; the tests still run on the wheels

    drive_base.reset()
    core.hub.imu.reset_heading(0)


def log_until_done(samples):
    """Record (ms, distance, speed) until the current move finishes."""
    while not drive_base.done():
        distance, speed, _, _ = drive_base.state()
        samples.append((timer.time(), distance, speed))
        wait(5)


def speeds_between(samples, low, high):
    return [speed for _, distance, speed in samples if low <= distance <= high]


def turn_to(target):
    """Turn by the shortest way from where the gyro says we ARE to `target`."""
    drive_base.turn((target - heading() + 180) % 360 - 180)


def finish(test, started):
    report(test, "took {0} ms, heading {1:.1f}, battery {2:.2f} V".format(
        timer.time() - started, heading(), voltage()))


# --- A: firmware ---------------------------------------------------------------
def test_firmware():
    report("A", "firmware {0}".format(version))
    report("A", "battery {0:.2f} V, defaults {1}".format(voltage(), DEFAULTS))

    checks = (
        ("straight(then=Stop.NONE)",
         lambda: drive_base.straight(0, then=Stop.NONE)),
        ("straight(wait=False)",
         lambda: drive_base.straight(0, wait=False)),
        ("turn(then=Stop.NONE)",
         lambda: drive_base.turn(0, then=Stop.NONE)),
        ("use_gyro()",
         lambda: drive_base.use_gyro(True)),
        ("done()",
         lambda: drive_base.done()),
        ("state()",
         lambda: drive_base.state()),
    )

    for name, check in checks:
        try:
            check()
            report("A", name + " OK")
        except (TypeError, AttributeError) as error:
            report("A", name + " MISSING -- {0}".format(error))

    drive_base.stop()


# --- B: wheel diameter ------------------------------------------------------------
def test_wheel():
    fresh()
    drive_base.straight(1000)

    report("B", "asked for 1000 mm. Measure the real distance, then:")
    report("B", "  WHEEL_DIAMETER_MM = {0} x real_mm / 1000".format(
        WHEEL_DIAMETER_MM))


# --- C: axle track ---------------------------------------------------------------
def test_axle():
    # on the wheels alone, so the gyro is a referee rather than the controller
    fresh(use_gyro=False)
    drive_base.turn(360)
    wait(500)                   # let the IMU settle before reading it

    turned = heading()
    report("C", "asked for 360, the gyro says {0:.1f}".format(turned))

    if turned:
        report("C", "  AXLE_TRACK_MM = {0:.1f}".format(
            AXLE_TRACK_MM * 360 / turned))


# --- D: is a split straight seamless? --------------------------------------------
def test_join():
    for label, split in (("one straight(600)", False),
                         ("straight(300, NONE) + straight(300)", True)):
        fresh()
        samples = []

        if split:
            drive_base.straight(300, then=Stop.NONE, wait=False)
            log_until_done(samples)
            drive_base.straight(300, wait=False)
        else:
            drive_base.straight(600, wait=False)

        log_until_done(samples)

        cruise = speeds_between(samples, 150, 250)
        join = speeds_between(samples, 250, 350)

        if cruise and join:
            report("D", "{0}: cruising {1} mm/s, slowest near 300 mm {2} mm/s"
                   .format(label, sum(cruise) // len(cruise), min(join)))
        else:
            report("D", "{0}: too few samples ({1})".format(label, len(samples)))

        # time to carry it back to the start line; the beep says it is going
        report("D", "put it back at the start -- the next part runs in 5 s")
        wait(5000)
        core.hub.speaker.beep()
        wait(500)

    report("D", "seamless if the two 'slowest' figures are about the same")


# --- E: settings() while rolling ----------------------------------------------------
def test_settings():
    fresh()
    samples = []

    drive_base.straight(300, then=Stop.NONE)   # returns while still rolling

    try:
        drive_base.settings(straight_speed=100)
        report("E", "settings() mid-motion ACCEPTED")
    except Exception as error:
        report("E", "settings() mid-motion REFUSED -- {0}".format(error))

    drive_base.straight(300, wait=False)
    log_until_done(samples)

    after = speeds_between(samples, 450, 550)

    if after:
        report("E", "speed after the change: {0} mm/s (asked for 100)".format(
            sum(after) // len(after)))

    drive_base.settings(*DEFAULTS)


# --- F: what is turn() relative to? ----------------------------------------------
def test_nudge():
    fresh()
    drive_base.turn(90, then=Stop.COAST)       # COAST, so it can be pushed

    report("F", "turned to {0:.1f}. TWIST THE ROBOT ~20 degrees by hand now"
           .format(heading()))
    core.hub.display.char("!")
    core.hub.speaker.beep()
    wait(4000)

    nudged = heading()
    report("F", "after the nudge: {0:.1f}".format(nudged))

    # without a real nudge both answers predict ~180, and the comparison
    # below would pick one on noise -- which it did, the first time
    if abs(nudged - 90) < 8:
        report("F", "NO NUDGE SEEN (under 8 degrees) -- run F again and "
               "twist harder, within 4 s of the beep")
        return

    drive_base.turn(90)
    wait(300)

    final = heading()
    report("F", "turned another 90, now at {0:.1f}".format(final))

    if abs(final - 180) < abs(final - (nudged + 90)):
        report("F", "turn() corrects back to its own target -- turn_to not needed")
    else:
        report("F", "turn() starts from the real heading -- 5.6 needs turn_to")


# --- H, I: the square two ways ----------------------------------------------------
def test_square_by():
    fresh()
    drive_base.settings(straight_speed=SQUARE_SPEED)
    started = timer.time()

    facing = 0

    for distance, target in SQUARE:
        drive_base.straight(distance)
        drive_base.turn((target - facing + 180) % 360 - 180)
        facing = target

    finish("H", started)


def test_square_to():
    fresh()
    drive_base.settings(straight_speed=SQUARE_SPEED)
    started = timer.time()

    for distance, target in SQUARE:
        drive_base.straight(distance)
        turn_to(target)

    finish("I", started)


# --- J: a run planned with a different wheel ------------------------------------
def _try(test, what, action):
    """Run one step of J, and say whether it worked."""
    try:
        result = action()
        report(test, what + " OK")
        return True, result
    except Exception as error:
        report(test, what + " FAILED -- " + repr(error))
        return False, None


def test_second_drive_base():
    """A run whose profile has a different wheel from config.py.

    The first version of this test asked whether configure() could build a
    second DriveBase for it. On the hub (2026-10-04, Pybricks 4.0.1) the
    answer was no -- OSError(16, 'Device or resource busy'): a motor belongs
    to one DriveBase for the whole program. So configure() now keeps
    config.py's wheel and track, prints a warning, and drives on. This
    checks exactly that: no error, the same DriveBase, a warning printed.

    Needs about 20 cm clear in front: it drives 100 mm forward and back.
    """
    fresh()
    first = core.drive_base

    worked, given = _try("J", "configure() with wheel +2 mm",
                         lambda: core.configure(wheel_diameter=WHEEL_DIAMETER_MM + 2,
                                                axle_track=AXLE_TRACK_MM))
    if not worked:
        return

    report("J", "kept the same DriveBase: {0}".format(given is first))
    _try("J", "driving 100 mm with it", lambda: given.straight(100))
    _try("J", "driving back with config.py's numbers",
         lambda: core.configure().straight(-100))
    report("J", "right if every line says OK, the DriveBase was kept, and a "
           "'planned with wheel' warning was printed above")


def after_test():
    drive_base.stop()
    core.setDriveTo(Stop.BRAKE)


report("-", "ready, battery {0:.2f} V".format(voltage()))

RunSelector(
    core,
    runs=[test_firmware, test_wheel, test_axle, test_join, test_settings,
          test_nudge, test_square_by, test_square_to, test_second_drive_base],
    labels=list("ABCDEFHIJ"),     # no G -- see the top of this file
    after=after_test,
    wrap=True,
).run_forever()
