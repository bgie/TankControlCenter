from PySide2.QtCore import QObject, Signal, Slot
import time

import platform
if platform.system() == 'Windows':
    import joystickapi_win as joystickapi
else:
    import joystickapi_linux as joystickapi

SNES_BUTTON_A = 0x01
SNES_BUTTON_B = 0x02
SNES_BUTTON_X = 0x04
SNES_BUTTON_Y = 0x08
SNES_BUTTON_L = 0x10
SNES_BUTTON_R = 0x20
SNES_BUTTON_SELECT = 0x40
SNES_BUTTON_START = 0x80
SNESS_BUTTONS_COUNT = 8

SNESS_LONG_BUTTON_PRESS_TIME_SEC = 2
ENUMERATE_JOYSTICKS_DELAY_SEC = 3

class Joystick(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._x = 0
        self._y = 0
        self._buttons = 0
        self._long_press_buttons = 0
        self._button_long_press_time = {}

    def x(self):
        return self._x

    def y(self):
        return self._y

    def buttons(self):
        return self._buttons

    def long_press_buttons(self):
        return self._long_press_buttons

    polled = Signal(int, int, int)
    changed = Signal(int, int, int)
    x_pressed = Signal(int)
    y_pressed = Signal(int)
    buttons_pressed = Signal(int)
    long_press_buttons_pressed = Signal(int)
    unplugged = Signal()

    def update(self, x, y, buttons):
        new_x = x if (x != self._x) else 0
        new_y = y if (y != self._y) else 0
        new_buttons = buttons & ~self._buttons

        long_press_buttons = 0
        current_time = time.time()
        for b in [1 << i for i in range(1, SNESS_BUTTONS_COUNT+1)]:
            if buttons & b:
                b_long_press_time = self._button_long_press_time.get(b)
                if b_long_press_time is None:
                    self._button_long_press_time[b] = current_time + SNESS_LONG_BUTTON_PRESS_TIME_SEC
                elif b_long_press_time <= current_time:
                    long_press_buttons = long_press_buttons | b
            else:
                self._button_long_press_time.pop(b, None)
        new_long_press_buttons = long_press_buttons & ~self._long_press_buttons

        has_changed = (x != self._x) or \
                      (y != self._y) or \
                      (buttons != self._buttons) or \
                      (long_press_buttons != self._long_press_buttons)

        self._x = x
        self._y = y
        self._buttons = buttons
        self._long_press_buttons = long_press_buttons

        self.polled.emit(x, y, buttons)
        if has_changed:
            self.changed.emit(x, y, buttons)
        if new_x:
            self.x_pressed.emit(new_x)
        if new_y:
            self.y_pressed.emit(new_y)
        if new_buttons:
            self.buttons_pressed.emit(new_buttons)
        if new_long_press_buttons:
            self.long_press_buttons_pressed.emit(new_long_press_buttons)

    def unplug(self):
        self.unplugged.emit()


class Joysticks(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._devices = None
        self._devices_cache = None
        self._joysticks = {}
        self._last_refresh = time.time()
        self._next_enumerate = time.time()
        self._refreshes = 0
        self.refresh()

    @Slot(result=float)
    def refreshesPerSecond(self):
        new_time = time.time()
        result = self._refreshes / (new_time - self._last_refresh)
        self._last_refresh = new_time
        self._refreshes = 0
        return result

    refreshed = Signal()
    added = Signal(Joystick)

    @Slot()
    def refresh(self):
        #if self._devices is None: # or self._next_enumerate <= time.time():
        #    self._next_enumerate = time.time() + ENUMERATE_JOYSTICKS_DELAY_SEC
        self._devices, self._devices_cache = joystickapi.enumerate_joysticks(self._devices, self._devices_cache)
        
        new_indices = set()
        self._devices, connected_joysticks = joystickapi.poll_joysticks(self._devices)
        
        for index, values in connected_joysticks.items():
            if index not in self._joysticks:
                self._joysticks[index] = Joystick()
                new_indices.add(index)
            x, y, buttons = values
            self._joysticks[index].update(x, y, buttons)
        
        missing_indices = self._joysticks.keys() - connected_joysticks.keys()
        for i in missing_indices:
            self._joysticks.pop(i).unplug()

        for i in new_indices:
            self.added.emit(self._joysticks[i])

        self._refreshes = self._refreshes + 1
        self.refreshed.emit()

    def joysticks(self):
        return self._joysticks.values()
