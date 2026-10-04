"""
Tunable values. Hardware ports and directions live in config.py instead.

Default units:
    voltage         volts
    angle           degrees
    time            seconds
"""

from pybricks.parameters import Button


# --- stop button ------------------------------------------------------------
# The hub normally uses CENTER to stop a running program. This template needs
# CENTER to start runs, so the stop button has to move somewhere else.
#
# BLUETOOTH keeps a real abort button, which matters: while a run is driving
# you want a way to kill it.
#
# Set this to None to free that button too -- but then the only way to stop a
# run is holding CENTER for three seconds, which powers the hub off.
STOP_BUTTON = Button.BLUETOOTH


# --- run behaviour ----------------------------------------------------------
# Reset the heading and task-motor encoders before every run. Almost always
# what you want: each run assumes it starts from a known zero.
zeroBeforeEveryRun = True

# Give the technician time to take their hands off the robot after pressing
# the button, so they do not nudge it as it starts.
takeHandsOff = True
time_to_take_hands_off = 0.6


# --- battery ----------------------------------------------------------------
# Motor power is scaled by MAX_VOLTAGE / current_voltage so that a run behaves
# the same on a full and a half-empty battery.
#
# Set this to what your hub reads at full charge. Measure it with:
#     print(hub.battery.voltage() / 1000)
# A SPIKE Prime Li-ion pack sits around 8.3 V full and 6.0 V empty, so 8.0 is a
# reasonable starting point. (The EV3 value was 7.5 for 6xAA -- do not reuse it.)
MAX_VOLTAGE = 8.0
