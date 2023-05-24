import math

import pynput
import pyautogui
from simple_pid import PID
import ctypes
# 鼠标移动 锁

pidx = PID(0.3, 0, 0.01, setpoint=0, sample_time=0)
pidy = PID(0, 0, 0, setpoint=0, sample_time=0)


PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput),]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

ii_ = Input_I()
extra = ctypes.c_ulong(0)

def ctypes_moveR(x0, y0):
    ii_.mi = MouseInput(x0, y0, 0, 0x0001, 0, ctypes.pointer(extra))
    command = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(command), ctypes.sizeof(command))


def lock(aims, mouse, x, y):
    mouse_pos_x, mouse_pos_y = mouse.position
    dist_list = []

    for det in aims:
        id, x_c, y_c, _, _ = det
        z = int(id)
        if z == 1 or z == 3:
            dist = max((2650 / 2 - x / 2 + x * float(x_c) - mouse_pos_x) ** 2 + (1600 / 2 - y / 2 + y * float(y_c) - mouse_pos_y) ** 2 - 900, 0)
        else:
            dist = (2650 / 2 - x / 2 + x * float(x_c) - mouse_pos_x) ** 2 + (1600 / 2 - y / 2 + y * float(y_c) - mouse_pos_y) ** 2

        dist_list.append(dist)
    # print(dist)
    if dist > 1000000:
        return
    det = aims[dist_list.index(min(dist_list))]

    tag, x_center, y_center, width, height = det
    tag = int(tag)
    x_center, width = x * float(x_center), x * float(width)
    y_center, height = y * float(y_center), y * float(height)


    # x_center = x_center + 2560 / 2 - 320 / 2
    # y_center = y_center + 1600 / 2 - 320 / 2
    # print(x_center, y_center)

    x_center = x_center - (640 // 2)
    y_center = y_center - (640 // 2)
    x_center = -int(pidx(x_center))
    y_center = -int(pidy(y_center))
    print(x_center, y_center)

    if tag == 1 or tag == 3:
        ctypes_moveR(x_center, y_center)
    elif tag == 0 or tag == 2:
        ctypes_moveR(x_center, y_center)
        # mouse.position = (x_center, y_center - 1 / 6 * height)
        # print(y_center - 1 / 6 * height)

# PID参数
kp = 0.5
ki = 0.01
kd = 0.01

# 初始误差和误差积分
error = 0
last_error = 0
integral = 0

# 鼠标移动 锁
# def lock1(aims, mouse, x, y):
#     mouse_pos_x, mouse_pos_y = mouse.position
#     dist_list = []
#
#     for det in aims:
#         id, x_c, y_c, _, _ = det
#         z = int(id)
#         if z == 1 or z == 3:
#             dist = max((2650 / 2 - x / 2 + x * float(x_c) - mouse_pos_x) ** 2 + (1600 / 2 - y / 2 + y * float(y_c) - mouse_pos_y) ** 2 - 900, 0)
#         else:
#             dist = (2650 / 2 - x / 2 + x * float(x_c) - mouse_pos_x) ** 2 + (1600 / 2 - y / 2 + y * float(y_c) - mouse_pos_y) ** 2
#
#         dist_list.append(dist)
#     det = aims[dist_list.index(min(dist_list))]
#
#     tag, x_center, y_center, width, height = det
#     tag = int(tag)
#     x_center, width = x * float(x_center), x * float(width)
#     y_center, height = y * float(y_center), y * float(height)
#
#     x_center = x_center + 2560 / 2 - 1080 / 2
#     y_center = y_center + 1600 / 2 - 1080 / 2
#
#     if tag == 1 or tag == 3:
#         mouse.position = (x_center, y_center)
#     elif tag == 0 or tag == 2:
#         mouse.position = (x_center, y_center - 1 / 6 * height)

# 压枪

import csv
import time
from threading import Thread


def recoil_control():
    f = csv.reader(open('./ammo_path/ak47.csv', encoding='utf-8'))
    ak_recoil = []
    for i in f:
        ak_recoil.append(i)
    ak_recoil[0][0] = '0'
    # 转换成 float
    ak_recoil = [[float(i) for i in x] for x in ak_recoil]
    print(ak_recoil)

    k = -1
    mouse = pynput.mouse.Controller()
    flag = 0

    recoil_mode = False  # mouse.button.x1 按下下侧键开始
    with pynput.mouse.Events() as events:
        for event in events:
            if isinstance(event, pynput.mouse.Events.Click):
                if event.button == event.button.left:
                    if event.pressed:
                        flag = 1
                    else:
                        flag = 0
                if event.button == event.button.right and event.pressed:  # 开始按钮 right 右键
                    recoil_mode = not recoil_mode
                    print('recoil mode1', 'on' if recoil_mode else 'off')

            if flag and recoil_mode:
                i = 0
                a = events.get()
                while True:
                    mouse.move(ak_recoil[i][0] * k, ak_recoil[i][1] * k)
                    i += 1

                    if i == 30:
                        break
                    if a is not None and isinstance(a,
                                                    pynput.mouse.Events.Click) and a.button == a.button.left and not a.pressed:
                        break
                    a = events.get()
                    while a is not None and not isinstance(a, pynput.mouse.Events.Click):
                        a = next(events)

                    time.sleep(ak_recoil[i][2] / 1000)
                flag = 0
