from PySide2.QtCore import QObject, Signal, Slot


class Foo(QObject):
    def __init__(self):
        QObject.__init__(self)

    bar = Signal(int)

    @Slot(int)
    def baz(self, i):
        print(i)
        return i


if __name__ == '__main__':
    f = Foo()
    f.bar.connect(f.baz)
    f.bar.emit(42)
    f.bar.disconnect(f.baz)
    f.bar.emit(666)
