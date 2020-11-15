import evdev
import glob


def map_snes_xy(value):
    if value < 32:
        return -1
    elif value > 196:
        return 1
    return 0


def map_snes_button(value):
    if 288 <= value <= 295:
        return 1 << (value - 288)
    return 0


def enumerate_joysticks(devices, checked_paths):
    if devices is None:
        devices = []
    if checked_paths is None:
        checked_paths = set()
    
    current_paths = set(glob.glob('/dev/input/event*'))
    
    devices = [device for device in devices if device.path in current_paths]

    new_paths = current_paths - checked_paths
    if checked_paths:
        not_ready_yet = set([p for p in new_paths if not evdev.util.is_device(p)])
        current_paths = set([p for p in current_paths if p not in not_ready_yet])
            
    for device in [evdev.InputDevice(path) for path in new_paths if evdev.util.is_device(path)]:
        caps = device.capabilities()
        if evdev.ecodes.EV_ABS in caps and \
           evdev.ecodes.EV_KEY in caps and \
           evdev.ecodes.BTN_JOYSTICK in caps[evdev.ecodes.EV_KEY]:
            devices.append(device)

    return devices, current_paths


def poll_joysticks(devices):
    joysticks = {}   
    
    for device in devices:
        key = device.path
        try:
            x = map_snes_xy(device.absinfo(evdev.ecodes.ABS_X).value)
            y = map_snes_xy(device.absinfo(evdev.ecodes.ABS_Y).value)
            buttons = 0
            for code in device.active_keys():
                buttons = buttons | map_snes_button(code)
            
        except OSError as o:
            devices.remove(device)
            
        else:
            joysticks[key] = (x, y, buttons)

    return devices, joysticks
