from PySide2.QtCore import QObject, Property, Signal, Slot
import joysticks


class Tank(QObject):
    def __init__(self, index, remote_control):
        QObject.__init__(self)
        self._index = index
        self._remote_control = remote_control
        self._connected = False
        self._joystick = None

    def name(self):
        return f"Tank {self._index}"

    name_changed = Signal()
    name = Property(str, name, notify=name_changed)

    def is_connected(self):
        return self._connected

    connected_changed = Signal()
    connected = Property(bool, is_connected, notify=connected_changed)

    def joystick(self):
        return self._joystick

    def is_joystick_assigned(self):
        return self._joystick is not None

    def set_joystick(self, j):
        if self._joystick != j:
            if self._joystick is not None:
                self._joystick.changed.disconnect(self.on_joystick_changed)
                self._joystick.long_press_buttons_pressed.disconnect(self.on_long_press_buttons_pressed)
            self._joystick = j
            if self._joystick is not None:
                self._joystick.changed.connect(self.on_joystick_changed)
                self._joystick.long_press_buttons_pressed.connect(self.on_long_press_buttons_pressed)
            self.joystick_assigned_changed.emit(self.is_joystick_assigned())

    joystick_assigned_changed = Signal(bool)
    joystickAssigned = Property(bool, is_joystick_assigned, notify=joystick_assigned_changed)

    @Slot(int, int, int)
    def on_joystick_changed(self, x, y, buttons):
        self._remote_control.send_move_command(self._index, x, y)

    @Slot(int)
    def on_long_press_buttons_pressed(self, buttons):
        if buttons & joysticks.SNES_BUTTON_SELECT:
            self.select_pressed.emit(self)

    select_pressed = Signal(QObject)

    @Slot(list)
    def onConnectionsChanged(self, ids):
        new_connected_status = self._index in ids
        if new_connected_status != self._connected:
            self._connected = new_connected_status
            self.connected_changed.emit()
