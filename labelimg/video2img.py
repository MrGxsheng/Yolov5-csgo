import os

import cv2


def save_image(addr, image, num):
    address = addr + 'img_' + str(num) + '.jpg'
    print(address)
    cv2.imwrite(address, image)


video_path = r'E:\yolov5-master\labelimg\video/1.mkv'
out_path = 'E:/yolov5-master/labelimg/images/'

# 是否取所有帧
is_all_frame = True
# 开始帧
sta_frame = 1
# 结束帧
end_frame = 1000

# 时间建间隔
time_interval = 60

# 读取视频
videocapture = cv2.VideoCapture(video_path)
success, frame = videocapture.read()

i = 0
j = 0

# 取最后图片最后一位
for root, dirs, files in os.walk(out_path):
    for filesPath in files:
        file = filesPath[:-4]
        file = file[4:]
        j = max(j, int(file))


while success:
    i += 1
    if i % time_interval == 0:
        if not is_all_frame:  # 不取所有帧
            if sta_frame <= i <= end_frame:
                j += 1
                print('save frame', j)
                save_image(out_path, frame, j)
            elif i > end_frame:
                break

        else:
            j += 1
            print('save frame', j)
            save_image(out_path, frame, j)

    success, frame = videocapture.read()
