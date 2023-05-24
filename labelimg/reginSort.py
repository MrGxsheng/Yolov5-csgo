import os

imgPath = 'E:/yolov5-master/labelimg/images/'
labelPath = 'E:/yolov5-master/labelimg/label/'
label = []

# 重新排序
for root, dirs, files in os.walk(labelPath):
    for filesPath in files:
        file = filesPath[:-4]
        file = file[4:]
        label.append(int(file))

list.sort(label)
i = 659

# 重命名
for j in label:
    oldLabel = 'img_' + str(j) + '.txt'
    oldImg = 'img_' + str(j) + '.jpg'
    newLabel = 'img_' + str(i) + '.txt'
    newImg = 'img_' + str(i) + '.jpg'

    os.rename(imgPath + oldImg, imgPath + newImg)
    os.rename(labelPath + oldLabel, labelPath + newLabel)

    i += 1


