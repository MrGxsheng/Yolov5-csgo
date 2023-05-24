import os
import time

os.getcwd()
os.add_dll_directory(os.path.abspath(os.path.dirname(__file__)))
from ctypes import windll
import cv2

windll.winmm.timeBeginPeriod(1)
stop = windll.kernel32.Sleep

# 把DXGI.pyd 复制到当前路径
import DXGI

g = DXGI.capture(600, 400, 1000, 800)  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)

while True:

    t =time.perf_counter()

    img = g.cap()

    print(time.perf_counter() - t)

    cv2.imshow('c',img)
    cv2.waitKey(1)

