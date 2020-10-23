from PySide2.QtCore import Qt, QUrl, QObject, Property, Signal, Slot
import time
import joystickapi


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
    disconnected = Signal()

    def update(self, x, y, buttons):
        new_x = x if (x != self._x) else 0
        new_y = y if (y != self._y) else 0
        new_buttons = buttons & ~self._buttons

        self._x = x
        self._y = y
        self._buttons = buttons
        self.changed.emit(x, y, buttons)

        if new_x:
            self.x_pressed.emit(new_x)
        if new_y:
            self.y_pressed.emit(new_y)
        if new_buttons:
            self.buttons_pressed.emit(new_buttons)

    def disconnect(self):
        self.disconnected.emit()


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
                x = joystickapi.map_snes_xy(info.dwXpos)
                y = joystickapi.map_snes_xy(info.dwYpos)
                buttons = info.dwButtons
                self._joysticks[i].update(x, y, buttons)

        missing_indices = self._joysticks.keys() - connected_indices
        for i in missing_indices:
            self._joysticks.pop(i).disconnect()

        for i in new_indices:
            self.added.emit(self._joysticks[i])

        self._refreshes = self._refreshes + 1
        self.refreshed.emit()

    def joysticks(self):
        return self._joysticks.values()