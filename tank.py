from PySide2.QtCore import QObject, Property, Signal, Slot


class Tank(QObject):
    def __init__(self, id):
        QObject.__init__(self)
        self._id = id
        self._connected = False
        self._joystick = None

    def name(self):
        return f"Tank {self._id}"

    name_changed = Signal()
    name = Property(str, name, notify=name_changed)

    def is_connected(self):
        return self._connected

    connected_changed = Signal()
    connected = Property(bool, is_connected, notify=connected_changed)

    def get_joystick(self):
        return self._joystick

    def is_joystick_assigned(self):
        return self._joystick is not None

    joystick_assigned_changed = Signal(bool)
    joystick_assigned = Property(bool, is_joystick_assigned, notify=joystick_assigned_changed)

    def set_joystick(self, joystick):
        self._joystick = joystick
        self.joystick_assigned_changed.emit(self.is_joystick_assigned())

    @Slot(list)
    def onConnectionsChanged(self, ids):
        new_connected_status = self._id in ids
        if new_connected_status != self._connected:
            self._connected = new_connected_status
            self.connected_changed.emit()
