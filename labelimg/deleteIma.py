import os

imgPath = r'E:\yolov5-master\labelimg\images'
labelPath = r'E:\yolov5-master\labelimg\label'
label = []

# 取打好的文件
for root, dirs, files in os.walk(labelPath):
    for filesPath in files:
        file = filesPath[:-4]
        file = file[4:]
        label.append(file)

# 删除没打标签的图片
for root, dirs, files in os.walk(imgPath):
    for filesPath in files:

        file = filesPath[:-4]
        file = file[4:]

        if file not in label:
            os.remove(imgPath + '\img_' + file + '.jpg')
