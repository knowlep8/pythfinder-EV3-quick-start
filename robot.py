"""
Core robot object for a SPIKE Prime / Robot Inventor hub.

Assumes the common FLL layout:
    - 2 driving motors            (required)
    - 2 task motors, for attachments   (optional)
    - up to 3 color sensors            (optional)
    - the hub's built-in IMU for heading -- no external gyro needed

Ports and directions come from config.py.
"""

from pybricks.hubs import PrimeHub
from pybricks.parameters import Stop
from pybricks.pupdevices import ColorSensor, Motor
from pybricks.robotics import DriveBase
from pybricks.tools import StopWatch

import config
from constants import MAX_VOLTAGE, STOP_BUTTON
from led import Led
from math_ex import clipMotor, normalizeDegrees


def _optional_motor(port, direction):
    """A task motor that may simply not be plugged in."""
    if port is None:
        return None
    try:
        return Motor(port, positive_direction=direction)
    except OSError:
        return None


def _optional_sensor(port):
    if port is None:
        return None
    try:
        return ColorSensor(port)
    except OSError:
        return None


class Robot:
    def __init__(self):
        # Describing the hub's mounting lets the IMU report a heading in robot
        # coordinates, which is what the old up_side_down / front_side_back
        # gyro flags were working around on the EV3.
        self.hub = PrimeHub(top_side=config.HUB_TOP_SIDE,
                            front_side=config.HUB_FRONT_SIDE)

        # CENTER stops a Pybricks program by default, which would kill the
        # program the moment RunSelector tried to use it to start a run.
        # Move the stop button out of the way -- see STOP_BUTTON in constants.
        self.hub.system.set_stop_button(STOP_BUTTON)

        # Drive motors are not optional -- without them there is no robot.
        try:
            self.leftDrive = Motor(config.LEFT_WHEEL_PORT,
                                   positive_direction=config.LEFT_WHEEL_DIRECTION)
            self.rightDrive = Motor(config.RIGHT_WHEEL_PORT,
                                    positive_direction=config.RIGHT_WHEEL_DIRECTION)
        except OSError:
            raise Exception("You need TWO (2) driving motors. Check config.py "
                            "-- expected LEFT on {0} and RIGHT on {1}"
                            .format(config.LEFT_WHEEL_PORT, config.RIGHT_WHEEL_PORT))

        self.leftTask = _optional_motor(config.LEFT_TASK_PORT,
                                        config.LEFT_TASK_DIRECTION)
        self.rightTask = _optional_motor(config.RIGHT_TASK_PORT,
                                         config.RIGHT_TASK_DIRECTION)

        self.leftColor = _optional_sensor(config.COLOR_SENSOR_LEFT_PORT)
        self.rightColor = _optional_sensor(config.COLOR_SENSOR_RIGHT_PORT)
        self.attachmentColor = _optional_sensor(config.ATTACHMENT_COLOR_SENSOR_PORT)

        self.led_control = Led(self.hub)

        # Every run drives with this. Pybricks allows one DriveBase per motor
        # for the whole program, so it is made once, here, from config.py.
        # (Direct dc() calls, as teleop.py makes, still take the motors back.)
        self.drive_base = DriveBase(self.leftDrive, self.rightDrive,
                                    config.WHEEL_DIAMETER_MM, config.AXLE_TRACK_MM)
        self.drive_base.use_gyro(True)
        self._geometry = (config.WHEEL_DIAMETER_MM, config.AXLE_TRACK_MM)
        self._default_settings = self.drive_base.settings()

        self.frequency_timer = StopWatch()
        self.start_loop_time = 0

        self.voltage = self.hub.battery.voltage() / 1000

    # --- power ------------------------------------------------------------
    def normalizeVoltage(self, power):
        """Scale power so a run behaves the same on a full or half-empty pack."""
        if self.voltage != 0:
            return power * MAX_VOLTAGE / self.voltage
        return power

    def setWheelPowers(self, left, right):
        self.leftDrive.dc(clipMotor(self.normalizeVoltage(left)))
        self.rightDrive.dc(clipMotor(self.normalizeVoltage(right)))

    def setDriveTo(self, stop_type):
        if stop_type is Stop.COAST:
            self.leftDrive.stop()
            self.rightDrive.stop()

        elif stop_type is Stop.BRAKE:
            self.leftDrive.brake()
            self.rightDrive.brake()

        elif stop_type is Stop.HOLD:
            self.leftDrive.hold()
            self.rightDrive.hold()

    def stopTaskMotors(self):
        if self.leftTask is not None:
            self.leftTask.stop()
        if self.rightTask is not None:
            self.rightTask.stop()

    # --- driving, for files from the web planner ---------------------------
    def configure(self, wheel_diameter=None, axle_track=None,
                  straight_speed=None, straight_acceleration=None,
                  turn_rate=None, turn_acceleration=None, use_gyro=True):
        """Set up the DriveBase for one run, and hand it back.

        A planner file passes its robot profile's numbers. The speeds are
        applied; anything left out goes back to its default, so one run's slow
        profile never leaks into the next run.

        The wheel and axle track are NOT changed: they stay config.py's.
        Pybricks allows one DriveBase per motor for the whole program -- a
        second one is refused with "Device or resource busy" (drivebase_test.py,
        test J) -- and they do not need changing anyway. A run's distances are
        real millimetres on the field, so what makes the robot drive them
        right is THIS robot's measured wheel and track, not the copy a run
        carries. If they disagree, the run's copy is stale, and it says so.
        """
        asked = (wheel_diameter or self._geometry[0],
                 axle_track or self._geometry[1])

        # a tenth of a mm either way is rounding in the run file, not a
        # different robot
        if (abs(asked[0] - self._geometry[0]) > 0.1 or
                abs(asked[1] - self._geometry[1]) > 0.1):
            print("this run was planned with wheel {0} / axle track {1}, but "
                  "this robot is {2} / {3} (config.py) -- driving with this "
                  "robot's. Update the robot profile in the planner."
                  .format(asked[0], asked[1], *self._geometry))

        speeds = (straight_speed, straight_acceleration,
                  turn_rate, turn_acceleration)

        self.drive_base.settings(*[default if asked is None else asked
                                   for asked, default in
                                   zip(speeds, self._default_settings)])
        self.drive_base.use_gyro(use_gyro)

        return self.drive_base

    def set_heading(self, degrees):
        """Tell the gyro which way the robot faces, in the planner's field
        headings (0 up the field, 90 to the right). turn_to() works in those
        same headings, so this has to be right before the first turn."""
        self.hub.imu.reset_heading(degrees)

    def turn_to(self, degrees, by):
        """Turn to face `degrees`, the way the planner planned it.

        Works from where the gyro says the robot really is, so a heading that
        drifted on the last drive is corrected here instead of carried into
        the next one. Every rotation that ends facing `degrees` is the
        shortest one plus some whole turns; this takes the one closest to
        `by`, the rotation the plan made. That is the shortest way when the
        plan turned the shortest way, and the long way round when a turn was
        planned backwards -- which sweeps a different part of the mat, so it
        matters which.
        """
        shortest = (degrees - self.hub.imu.heading() + 180) % 360 - 180
        whole_turns = round((by - shortest) / 360)

        self.drive_base.turn(shortest + 360 * whole_turns)

    # --- zeroing ----------------------------------------------------------
    def zeroTaskMotors(self, resetLeft=True, resetRight=True):
        if resetLeft and self.leftTask is not None:
            self.leftTask.reset_angle(0)
        if resetRight and self.rightTask is not None:
            self.rightTask.reset_angle(0)

    def zeroGyro(self):
        self.hub.imu.reset_heading(0)

    def zero(self):
        self.zeroGyro()
        self.zeroTaskMotors()

    # --- state ------------------------------------------------------------
    def getHeading(self):
        # imu.heading() accumulates past 360 just like the EV3 gyro did, so it
        # still needs wrapping before findShortestPath() can use it.
        return normalizeDegrees(self.hub.imu.heading())

    def update(self, loop_time=False):
        self.voltage = self.hub.battery.voltage() / 1000

        if loop_time:
            end_loop_time = self.frequency_timer.time()
            elapsed = end_loop_time - self.start_loop_time
            if elapsed > 0:
                print("Frequency: {:.2f} loops / second".format(1000 / elapsed))
            self.start_loop_time = end_loop_time

    def showcaseAngle(self):
        print("angle (deg): {0}".format(self.getHeading()))

    def showcaseVoltage(self):
        print("V: {0}".format(self.voltage))
