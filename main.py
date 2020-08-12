import os, sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt, QUrl, QObject, Property, Signal, Slot

import joystickapi


class Joysticks(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._ids = set()
        self._buttons = {}
        self._x = {}
        self._y = {}
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

    refreshed = Signal()

    @Slot()
    def refresh(self):
        ids = set()
        buttons = {}
        x = {}
        y = {}

        for id in range(joystickapi.joyGetNumDevs()):
            ret, info = joystickapi.joyGetPosEx(id)
            if ret:
                ids.add(id)
                buttons[id] = info.dwButtons
                x[id] = joystickapi.map_snes_xy(info.dwXpos)
                y[id] = joystickapi.map_snes_xy(info.dwYpos)

        if ids != self._ids:
            self._ids = ids
            self.count_changed.emit()

        self._buttons = buttons
        self._x = x
        self._y = y
        self.refreshed.emit()


if __name__ == '__main__':
    #Set up the application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Expose Python object to QML
    joysticks = Joysticks()
    context = engine.rootContext()
    context.setContextProperty("Joysticks", joysticks)

    #Load the QML file
    qmlFile = os.path.join(os.path.dirname(__file__),"view.qml")
    engine.load(os.path.abspath(qmlFile))
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
