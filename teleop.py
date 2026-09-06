"""
Drive the robot from a game controller, to test attachments and the
drivetrain without writing a run.

Run this file instead of main.py.

The EV3 version read raw PS3/PS4 events out of /dev/input/event4. The hub has
no such device, and Pybricks only speaks to Xbox controllers, so this is an
Xbox rewrite. Turn the controller on and it will pair automatically.

Control scheme (same shape as the EV3 one):
    X                select the LEFT task motor
    B                select the RIGHT task motor
    left stick  Y    drive forwards / backwards
    right stick X    turn
    D-pad up         run the selected task motor forwards
    D-pad down       run the selected task motor backwards
    D-pad left       stop the selected task motor
"""

from pybricks.iodevices import XboxController
from pybricks.parameters import Button, Color
from pybricks.tools import wait

from edge_detector import EdgeDetectorEx
from robot import Robot


# --- tune these -------------------------------------------------------------
power_dc = 100              # (0, 100]  power given to a task motor
max_linear_power_dc = 100   # same range, forward / backward axis
max_angular_power_dc = 50   # same range, rotational axis

# D-pad values, following the usual 0-8 clock: 0 released, 1 up, 3 right,
# 5 down, 7 left.
DPAD_UP = 1
DPAD_DOWN = 5
DPAD_LEFT = 7


core = Robot()
core.led_control.setColor(Color.RED)

print("\n\nlooking for an Xbox controller...")
controller = XboxController()
print("connected to {0}".format(controller.name()))
core.led_control.setColor(Color.GREEN)

positive_detector = EdgeDetectorEx()
negative_detector = EdgeDetectorEx()
stop_detector = EdgeDetectorEx()

selected_task_motor = 'left'


def task_motor():
    """The motor the D-pad currently drives, or None if it is not fitted."""
    if selected_task_motor == 'left':
        return core.leftTask
    return core.rightTask


while True:
    pressed = controller.buttons.pressed()

    if Button.X in pressed:
        selected_task_motor = 'left'
    elif Button.B in pressed:
        selected_task_motor = 'right'

    dpad = controller.dpad()

    positive_detector.set(dpad == DPAD_UP)
    negative_detector.set(dpad == DPAD_DOWN)
    stop_detector.set(dpad == DPAD_LEFT)

    positive_detector.update()
    negative_detector.update()
    stop_detector.update()

    # Edge-triggered, so a tap latches the motor on until it is stopped --
    # the same behaviour the EV3 version had.
    motor = task_motor()
    if motor is not None:
        if positive_detector.rising:
            motor.dc(power_dc)
        elif negative_detector.rising:
            motor.dc(-power_dc)
        elif stop_detector.rising:
            motor.dc(0)

    # Sticks already arrive as -100..100 percentages, so no rescaling needed.
    _, linear = controller.joystick_left()
    angular, _ = controller.joystick_right()

    linear = linear * max_linear_power_dc / 100
    angular = angular * max_angular_power_dc / 100

    core.setWheelPowers(linear - angular, linear + angular)

    wait(10)
