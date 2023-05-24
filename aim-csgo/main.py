import time

import win32con
import win32gui
import torch
import cv2
import numpy as np
import pynput
from cs_model import load_model
from grabscreen import grab_screen
from utils.general import non_max_suppression, scale_boxes, xyxy2xywh
from utils.augmentations import letterbox
from mouse_control import lock, recoil_control
from threading import Thread
import DXGI

# # 截屏范围 0-分辨率
# a = grab_screen(region=(0, 0, 2560, 1600))
# cv2.imshow('1', a)
# cv2.waitKey(0)


imgsz = 640
conf_thres = 0.4
iou_thres = 0.45

model = load_model()
# half = device != 'cpu'
names = model.names
mouse = pynput.mouse.Controller()

x, y = (2560, 1600)
h, w = (640, 640)

x1, y1, x2, y2 = (int(x / 2 - w / 2), int(y / 2 - h / 2), int(x / 2 + w / 2), int(y / 2 + h / 2))
print(x1, y1, x2, y2)

re_x, re_y = (h, w)

lock_mode = False
g = DXGI.capture(x1, y1, x2, y2)  # 屏幕左上角 到 右下角  （x1, y1 ,x2 ,y2)


t = Thread(target=recoil_control)
t.start()

name = True  # T

#  非阻塞版本
# def on_move(x, y):
#     pass
#
#
# def on_click(x, y, button, pressed):
#     global lock_mode
#     if pressed and button == button.right:
#         lock_mode = not lock_mode
#         print("lock mode" , 'on' if lock_mode else 'off')
#
# def on_scroll(x, y, dx, dy):
#     pass
#
#
# listener = pynput.mouse.Listener(
#     on_move=on_move,
#     on_click=on_click,
#     on_scroll=on_scroll)
# listener.start()
# 阻塞版本
with pynput.mouse.Events() as events:
    while True:
        it = next(events)
        while it is not None and not isinstance(it, pynput.mouse.Events.Click):
            it = next(events)
        if it is not None and it.button == it.button.right and it.pressed:
            lock_mode = not lock_mode
            print('lock mode', 'on' if lock_mode else 'off')

        # while True:
        # img0 = grab_screen(region=(0, 0, x, y))
        # img0 = cv2.resize(img0, (re_x, re_y))
        img0 = g.cap()

        img = letterbox(img0, imgsz, stride=model.stride, auto=True)[0]
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)  # contiguous

        # 对图片的格式进行操作
        img = torch.from_numpy(img).to(model.device)
        img = img.half() if model.fp16 else img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim  img = img.unsqueeze(0)

        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, iou_thres, None, agnostic=False)
        a = time.time_ns() / 1000000

        aims = []

        # Process predictions
        for i, det in enumerate(pred):  # per image
            s = ''
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], img0.shape).round()

                for c in det[:, 5].unique():
                    n = (det[:, 5] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                    # Write results
                    for *xyxy, conf, cls in reversed(det):
                        # bbox:(tag,x_center,y_center,x_width,y_width)
                        """
                        0: CT_BODY 1: CT_HEAD 2: T_BODY 3: T_HEAD
                        """
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh)  # label format
                        aim = ('%g ' * len(line)).rstrip() % line
                        aim = aim.split(' ')
                        # print(aim)
                        z = int(aim[0])
                        if name:
                            if z == 0:
                                aims.append(aim)
                            if z == 1:
                                aims.append(aim)
                        else:
                            if z == 2:
                                aims.append(aim)
                            if z == 3:
                                aims.append(aim)

                if len(aims):
                    if lock_mode:
                        lock(aims, mouse, w, h )
                    for i, det in enumerate(aims):
                        _, x_center, y_center, width, height = det
                        x_center, width = re_x * float(x_center), re_x * float(width)
                        y_center, height = re_y * float(y_center), re_y * float(height)
                        top_left = (int(x_center - width / 2.), int(y_center - height / 2.))
                        bottom_right = (int(x_center + width / 2.), int(y_center + height / 2.))
                        color = (0, 255, 0)  # RGB
                        cv2.rectangle(img0, top_left, bottom_right, color, 3)

        cv2.namedWindow('csgo-detect', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('csgo-detect', re_x // 3, re_y // 3)
        cv2.imshow('csgo-detect', img0)

        hwnd = win32gui.FindWindow(None, 'csgo-detect')
        CVRECT = cv2.getWindowImageRect('csgo-detect')
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        # b = time.time_ns() / 1000000
        # print(b - a)


        # 按q 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
