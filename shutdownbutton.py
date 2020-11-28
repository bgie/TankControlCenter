import os
import joysticks
import time
from PySide2.QtCore import QObject, Slot

SHUTDOWN_BUTTONS_COMBO = joysticks.SNES_BUTTON_SELECT | joysticks.SNES_BUTTON_L | joysticks.SNES_BUTTON_R


class ShutdownButton(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._long_button_event_timeout = time.time()
        self._pressed_buttons = 0

    @Slot(joysticks.Joystick)
    def on_joystick_added(self, joystick):
        joystick.long_press_buttons_pressed.connect(self.on_long_press_buttons_pressed)

    @Slot(int, int)
    def on_long_press_buttons_pressed(self, long_press_buttons):
        now = time.time()

        if long_press_buttons & SHUTDOWN_BUTTONS_COMBO:
            if self._long_button_event_timeout > now:
                self._long_button_event_timeout = now + 1
                self._pressed_buttons = self._pressed_buttons | long_press_buttons
                if self._pressed_buttons & SHUTDOWN_BUTTONS_COMBO == SHUTDOWN_BUTTONS_COMBO:
                    os.system("shutdown /s /t 1")
            else:
                self._long_button_event_timeout = now + 1
                self._pressed_buttons = long_press_buttons
