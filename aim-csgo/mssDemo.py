import numpy as np
import cv2
import mss
import time
import keyboard

# 指定截图区域为屏幕中心的正方形区域
size = 300  # 正方形边长

left = int((mss.mss().monitors[0]['width'] - size) / 2)
top = int((mss.mss().monitors[0]['height'] - size) / 2)
right = left + size
bottom = top + size

running = True

while running:
    with mss.mss() as sct:
        start_time = time.perf_counter()
        # 保存截图
        monitor = {'left': left, 'top': top, 'width': size, 'height': size}
        sct_img = sct.grab(monitor)

        # 将截图转换为OpenCV可处理的格式
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # 显示截图
        cv2.imshow("screenshot", img)
        end_time = time.perf_counter()
        cv2.waitKey(1)
        duration = end_time - start_time
        print("程序用时：", duration, " 秒")
        if keyboard.is_pressed("F12"):
            running = False  # 设置变量以跳出循环或停止程序

cv2.destroyAllWindows()
