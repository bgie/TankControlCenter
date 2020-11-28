from PySide2.QtCore import QObject, Property, Signal, Slot
import joysticks


class TankSelector(QObject):
    def __init__(self, rows, columns, selection, joystick, x=0, y=0):
        QObject.__init__(self)
        self._rows = rows
        self._columns = columns
        self._selection = selection
        self._joystick = None
        self.set_joystick(joystick)
        self._x = x
        self._y = y
        self._select()

    def clear(self):
        self._selection.box_at_xy(self._x, self._y).clear_selector(self)

    def _select(self):
        self._selection.box_at_xy(self._x, self._y).set_selector(self)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def set_x(self, i: int):
        if self._x != i:
            self.clear()
            self._x = i
            self._select()

    def set_y(self, i: int):
        if self._y != i:
            self.clear()
            self._y = i
            self._select()

    def joystick(self):
        return self._joystick

    def set_joystick(self, j):
        if self._joystick != j:
            if self._joystick is not None:
                self._joystick.x_pressed.disconnect(self.on_x_pressed)
                self._joystick.y_pressed.disconnect(self.on_y_pressed)
                self._joystick.buttons_pressed.disconnect(self.on_buttons_pressed)
                self._joystick.unplugged.disconnect(self.on_unplugged)
            self._joystick = j
            if self._joystick is not None:
                self._joystick.x_pressed.connect(self.on_x_pressed)
                self._joystick.y_pressed.connect(self.on_y_pressed)
                self._joystick.buttons_pressed.connect(self.on_buttons_pressed)
                self._joystick.unplugged.connect(self.on_unplugged)

    @Slot(int)
    def on_x_pressed(self, joystick_x):
        self.set_x((self._x + joystick_x) % self._columns)

    @Slot(int)
    def on_y_pressed(self, joystick_y):
        self.set_y((self._y + joystick_y) % self._rows)

    @Slot(int)
    def on_buttons_pressed(self, buttons):
        if buttons & joysticks.SNES_BUTTON_START:
            self._selection.on_start_pressed(self)

    @Slot()
    def on_unplugged(self):
        self._selection.on_unplugged(self)


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
    def __init__(self, rows, columns, tanks):
        QObject.__init__(self)
        self._rows = rows
        self._columns = columns
        self._selectors = set()
        self._boxes = []
        for y in range(0, rows):
            for x in range(0, columns):
                self._boxes.append(SelectionBox(x, y))
        self._tanks = tanks
        for t in tanks:
            t.select_pressed.connect(self.on_tank_select_pressed)

    @Slot(joysticks.Joystick)
    def on_joystick_added(self, joystick):
        selector = TankSelector(self._rows, self._columns, self, joystick)
        self._selectors.add(selector)

    def on_start_pressed(self, selector: TankSelector):
        tank = self._tanks[self._index(selector.x(), selector.y())]
        joystick = selector.joystick()

        selector.clear()
        selector.set_joystick(None)
        self._selectors.remove(selector)
        tank.set_joystick(joystick)
        
    def on_unplugged(self, selector: TankSelector):
        joystick = selector.joystick()
        selector.clear()
        selector.set_joystick(None)
        self._selectors.remove(selector)

    def on_tank_select_pressed(self, tank):
        x, y = self._xy(self._tanks.index(tank))
        joystick = tank.joystick()
        tank.set_joystick(None)
        selector = TankSelector(self._rows, self._columns, self, joystick, x, y)
        self._selectors.add(selector)

    def _index(self, x, y):
        return x + (y * self._columns)
    
    def _xy(self, index):
        return index % self._columns, index // self._columns

    def box_at_xy(self, x, y):
        return self._boxes[self._index(x, y)]

    @Slot(int, result=SelectionBox)
    def box_at_index(self, index):
        return self._boxes[index]