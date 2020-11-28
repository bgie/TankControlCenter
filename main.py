import os, sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2 import QtCore

import joysticks
import remotecontrol
import tank
import tankselection
import shutdownbutton


def qt_message_handler(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        mode = 'Info'
    elif mode == QtCore.QtWarningMsg:
        mode = 'Warning'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'critical'
    elif mode == QtCore.QtFatalMsg:
        mode = 'fatal'
    else:
        mode = 'Debug'
    print("%s: %s (%s:%d, %s)" % (mode, message, context.file, context.line, context.file))


if __name__ == '__main__':
    # Set up the application
    QtCore.qInstallMessageHandler(qt_message_handler)
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Expose Python object to QML
    joysticks = joysticks.Joysticks()
    remote_control = remotecontrol.RemoteControl()

    context = engine.rootContext()
    context.setContextProperty("Joysticks", joysticks)
    context.setContextProperty("RemoteControl", remote_control)

    tank_list = []
    TANK_ROWS = 2
    TANK_COLUMNS = 2
    for index in range(1, TANK_ROWS * TANK_COLUMNS + 1):
        t = tank.Tank(index, remote_control)
        remote_control.connections_changed.connect(t.onConnectionsChanged)
        tank_list.append(t)
    context.setContextProperty("Tanks", tank_list)
    context.setContextProperty("TankRows", TANK_ROWS)
    context.setContextProperty("TankColumns", TANK_COLUMNS)

    button = shutdownbutton.ShutdownButton()
    joysticks.added.connect(button.on_joystick_added)

    tank_selection = tankselection.TankSelection(TANK_ROWS, TANK_COLUMNS, tank_list)
    joysticks.added.connect(tank_selection.on_joystick_added)
    for j in joysticks.joysticks():
        tank_selection.on_joystick_added(j)
        button.on_joystick_added(j)
    context.setContextProperty("TankSelection", tank_selection)

    # Load the QML file
    qmlFile = os.path.join(os.path.dirname(__file__), "view.qml")
    engine.load(os.path.abspath(qmlFile))
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
