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
from pybricks.tools import StopWatch

import config
from constants import MAX_VOLTAGE
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

        self.PID_multiplier = config.PID_MULTIPLIER

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
