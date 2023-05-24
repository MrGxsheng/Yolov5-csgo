from models.common import DetectMultiBackend
from utils.torch_utils import select_device

from utils.general import check_img_size

device = ''
half = device != 'cpu'
dnn = False  # use OpenCV DNN for ONNX inference

# 模型地址
weights = r'E:\yolov5-master\aim-csgo\models\best.engine'
data = r'E:\yolov5-master\data\mydata.yaml'
imgsz = (640, 640)


def load_model():
    device1 = select_device(device)

    model = DetectMultiBackend(weights, device=device1, dnn=dnn, data=data, fp16=True)


    model.warmup(imgsz=(1, 3, *imgsz))  # warmup

    return model
