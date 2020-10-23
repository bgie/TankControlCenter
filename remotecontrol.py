from PySide2.QtCore import Qt, QUrl, QObject, Property, Signal, Slot
import socket
import time

DISCOVER_REFRESH_SEC = 0.500
DISCOVER_TIMEOUT_SEC = 3.000
REFRESH_MOTOR_COMMAND_TIMEOUT_SEC = 0.200
TANK_UDP_PORT = 8001
CONTROLCENTER_UDP_PORT = 8002

class RemoteControl(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._udpSender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._udpSender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._udpSender.settimeout(0.2)

        self._udpListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._udpListener.setblocking(0)
        self._udpListener.bind(("", CONTROLCENTER_UDP_PORT))

        self._udpCommandSender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._udpCommandSender.settimeout(0.2)

        self._discover_timeout_time = time.time()
        self._robots = {}
        self._ids = set()

        self._motors = {}

    discovered = Signal()

    @Slot()
    def discover(self):
        current_time = time.time()
        if current_time > self._discover_timeout_time:
            self._discover_timeout_time = current_time + DISCOVER_REFRESH_SEC
            self._udpSender.sendto(b"HI", ("<broadcast>", TANK_UDP_PORT))

        try:
            data, addr = self._udpListener.recvfrom(1024)
            self._robots[int(data.decode('ascii'))] = (addr, current_time + DISCOVER_TIMEOUT_SEC)
        except socket.error:
            pass

        ids = set()
        for i, (addr, expire_time) in self._robots.items():
            if current_time < expire_time:
                ids.add(i)

        if ids != self._ids:
            self._ids = ids
            self.discovered.emit()
            self.connections_changed.emit(list(ids))

    def joystick_to_motor(x, y):
        if x == 0 and y == 0:
            return (0,0)
        if x == 0:
            return (y*-1024, y*-1024)
        if x < 0:
            if y == 0:
                return (-1024, 1024)
            else:
                return (0, y*-1024)
        if x > 0:
            if y == 0:
                return (1024, -1024)
            else:
                return (y*-1024, 0)

    @Slot(int, int, int, int)
    def moveTank(self, i, buttons, x, y):
        if i in self._ids:
            current_time = time.time()
            old_x, old_y, refresh_motor_command_time = self._motors.get(i, (0, 0, current_time))
            isMoving = (x != 0) or (y != 0)
            needsUpdate = (x != old_x) or (y != old_y) or (isMoving and refresh_motor_command_time < current_time)
            if needsUpdate:
                self._motors[i] = (x, y, current_time + REFRESH_MOTOR_COMMAND_TIMEOUT_SEC)
                left, right = RemoteControl.joystick_to_motor(x, y)
                motor_command = (f"MOTOR {left} {right}").encode('ascii')
                addr, _ = self._robots[i]
                self._udpCommandSender.sendto(motor_command, (addr[0], TANK_UDP_PORT))

    @Slot(int, result=bool)
    def connected(self, i):
        return i in self._ids

    connections_changed = Signal(list)
