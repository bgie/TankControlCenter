from PySide2.QtCore import Qt, QUrl, QObject, Property, Signal, Slot
import time
import joystickapi


class Joysticks(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._ids = set()
        self._buttons = {}
        self._x = {}
        self._y = {}
        self._lastRefresh = time.time()
        self._refreshes = 0
        self.refresh()

    def _count(self):
        return len(self._ids)

    count_changed = Signal()
    count = Property(int, _count, notify=count_changed)

    @Slot(int, result=bool)
    def connected(self, id):
        return id in self._ids

    @Slot(int, result=int)
    def buttons(self, id):
        return self._buttons[id]

    @Slot(int, result=int)
    def x(self, id):
        return self._x[id]

    @Slot(int, result=int)
    def y(self, id):
        return self._y[id]

    @Slot(result=float)
    def refreshesPerSecond(self):
        newtime = time.time()
        result = self._refreshes / (newtime - self._lastRefresh)
        self._lastRefresh = newtime
        self._refreshes = 0
        return result

    refreshed = Signal()
    joystickChanged = Signal(int, int, int, int)

    @Slot()
    def refresh(self):
        ids = set()
        buttons = {}
        x = {}
        y = {}

        for i in range(joystickapi.joyGetNumDevs()):
            ret, info = joystickapi.joyGetPosEx(i)
            if ret:
                ids.add(i+1)
                buttons[i+1] = info.dwButtons
                x[i+1] = joystickapi.map_snes_xy(info.dwXpos)
                y[i+1] = joystickapi.map_snes_xy(info.dwYpos)

        emit_count_changed = (ids != self._ids)

        self._ids = ids
        self._buttons = buttons
        self._x = x
        self._y = y
        self._refreshes = self._refreshes + 1

        if emit_count_changed:
            self.count_changed.emit()
        for i in ids:
            self.joystickChanged.emit(i, buttons[i], x[i], y[i])
        self.refreshed.emit()
