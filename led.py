"""Status-light control, mapped onto the hub's single RGB button light."""

from pybricks.parameters import Color


# Set any of these to None to turn the light off for that state instead.
default_NOT_STARTED_color = Color.RED
default_TAKE_YOUR_HANDS_OFF_color = Color.ORANGE
default_IN_PROGRESS_color = Color.GREEN


class Led():
    def __init__(self, hub):
        self.__hub = hub

        self.__not_started_color = default_NOT_STARTED_color
        self.__take_your_hands_off_color = default_TAKE_YOUR_HANDS_OFF_color
        self.__in_progress_color = default_IN_PROGRESS_color

    def addNotStartedColor(self, color):
        self.__not_started_color = color
        return self

    def addTakeYourHandsOffColor(self, color):
        self.__take_your_hands_off_color = color
        return self

    def addInProgressColor(self, color):
        self.__in_progress_color = color
        return self

    def __set(self, color):
        if color is None:
            self.__hub.light.off()
        else:
            self.__hub.light.on(color)

    def not_started(self):
        self.__set(self.__not_started_color)

    def take_your_hands_off(self):
        self.__set(self.__take_your_hands_off_color)

    def in_progress(self):
        self.__set(self.__in_progress_color)

    def off(self):
        self.__hub.light.off()

    def setColor(self, color):
        self.__hub.light.on(color)
