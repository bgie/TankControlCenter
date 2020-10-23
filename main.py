import os, sys
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import Qt

import joysticks
import remotecontrol

if __name__ == '__main__':
    # Set up the application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Expose Python object to QML
    joysticks = joysticks.Joysticks()
    remote_control = remotecontrol.RemoteControl()
    joysticks.joystickChanged.connect(remote_control.moveTank)

    context = engine.rootContext()
    context.setContextProperty("Joysticks", joysticks)
    context.setContextProperty("RemoteControl", remote_control)
    context.setContextProperty("Tanks", 3)

    # Load the QML file
    qmlFile = os.path.join(os.path.dirname(__file__), "view.qml")
    engine.load(os.path.abspath(qmlFile))
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
