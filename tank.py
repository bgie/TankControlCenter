from PySide2.QtCore import QObject, Property, Signal, Slot


class Tank(QObject):
    def __init__(self, id):
        QObject.__init__(self)
        self._id = id
        self._connected = False

    def _name(self):
        return f"Tank {self._id}!"

    name_changed = Signal()
    name = Property(str, _name, notify=name_changed)

    def _get_connected(self):
        return self._connected

    connected_changed = Signal()
    connected = Property(bool, _get_connected, notify=connected_changed)

    @Slot(list)
    def onConnectionsChanged(self, ids):
        new_connected_status = self._id in ids
        if new_connected_status != self._connected:
            self._connected = new_connected_status
            self.connected_changed.emit()
