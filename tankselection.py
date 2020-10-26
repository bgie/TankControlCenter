from PySide2.QtCore import QObject, Property, Signal, Slot
import joysticks


class TankSelector(QObject):
    def __init__(self, rows, columns, selection):
        QObject.__init__(self)
        self._x = 0
        self._y = 0
        self._rows = rows
        self._columns = columns
        self._selection = selection

    def set_x(self, i: int):
        if self._x != i:
            self._selection.box_at_xy(self._x, self._y).clear_selector(self)
            self._x = i
            self._selection.box_at_xy(self._x, self._y).set_selector(self)

    def set_y(self, i: int):
        if self._y != i:
            self._selection.box_at_xy(self._x, self._y).clear_selector(self)
            self._y = i
            self._selection.box_at_xy(self._x, self._y).set_selector(self)

    @Slot(int)
    def on_x_pressed(self, joystick_x):
        self.set_x((self._x + joystick_x) % self._columns)

    @Slot(int)
    def on_y_pressed(self, joystick_y):
        self.set_y((self._y + joystick_y) % self._rows)


class SelectionBox(QObject):
    def __init__(self, x, y):
        QObject.__init__(self)
        self._x = x
        self._y = y
        self._selectors = set()

    def is_selected(self):
        return len(self._selectors) > 0

    def set_selector(self, selector):
        if selector not in self._selectors:
            self._selectors.add(selector)
            self.selected_changed.emit(True)

    def clear_selector(self, selector):
        if selector in self._selectors:
            self._selectors.discard(selector)
            if len(self._selectors) == 0:
                self.selected_changed.emit(False)

    selected_changed = Signal(bool)
    selected = Property(int, is_selected, notify=selected_changed)


class TankSelection(QObject):
    def __init__(self, rows, columns):
        QObject.__init__(self)
        self._rows = rows
        self._columns = columns
        self._selectors = set()
        self._boxes = []
        for y in range(0, rows):
            for x in range(0, columns):
                self._boxes.append(SelectionBox(x, y))

    @Slot(joysticks.Joystick)
    def on_joystick_added(self, joystick):
        selector = TankSelector(self._rows, self._columns, self)
        joystick.x_pressed.connect(selector.on_x_pressed)
        joystick.y_pressed.connect(selector.on_y_pressed)
        self._selectors.add(selector)

    def box_at_xy(self, x, y):
        index = x + (y * self._columns)
        return self._boxes[index]

    @Slot(int, result=SelectionBox)
    def box_at_index(self, index):
        return self._boxes[index]