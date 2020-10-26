from PySide2.QtCore import QObject, Signal, Slot
import time
import joystickapi


SNES_BUTTON_A = 0x01
SNES_BUTTON_B = 0x02
SNES_BUTTON_X = 0x04
SNES_BUTTON_Y = 0x08
SNES_BUTTON_L = 0x10
SNES_BUTTON_R = 0x20
SNES_BUTTON_SELECT = 0x40
SNES_BUTTON_START = 0x80


def map_snes_xy(value):
    if value < 128:
        return -1
    elif value > 65407:
        return 1
    return 0


class Joystick(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._buttons = 0
        self._x = 0
        self._y = 0

    def x(self):
        return self._x

    def y(self):
        return self._y

    def buttons(self):
        return self._buttons

    changed = Signal(int, int, int)
    x_pressed = Signal(int)
    y_pressed = Signal(int)
    buttons_pressed = Signal(int)
    unplugged = Signal()

    def update(self, x, y, buttons):
        new_x = x if (x != self._x) else 0
        new_y = y if (y != self._y) else 0
        new_buttons = buttons & ~self._buttons

        has_changed = (x != self._x) or (y != self._y) or (buttons != self._buttons)

        self._x = x
        self._y = y
        self._buttons = buttons

        if has_changed:
            self.changed.emit(x, y, buttons)
        if new_x:
            self.x_pressed.emit(new_x)
        if new_y:
            self.y_pressed.emit(new_y)
        if new_buttons:
            self.buttons_pressed.emit(new_buttons)

    def unplug(self):
        self.unplugged.emit()


class Joysticks(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._joysticks = {}
        self._last_refresh = time.time()
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
        connected_indices = set()
        new_indices = set()

        for i in range(joystickapi.joyGetNumDevs()):
            ret, info = joystickapi.joyGetPosEx(i)
            if ret:
                connected_indices.add(i)
                if i not in self._joysticks:
                    self._joysticks[i] = Joystick()
                    new_indices.add(i)
                x = map_snes_xy(info.dwXpos)
                y = map_snes_xy(info.dwYpos)
                buttons = info.dwButtons
                self._joysticks[i].update(x, y, buttons)

        missing_indices = self._joysticks.keys() - connected_indices
        for i in missing_indices:
            self._joysticks.pop(i).unplug()

        for i in new_indices:
            self.added.emit(self._joysticks[i])

        self._refreshes = self._refreshes + 1
        self.refreshed.emit()

    def joysticks(self):
        return self._joysticks.values()
