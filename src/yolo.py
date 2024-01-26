from ultralytics import YOLO
from PIL import Image

model = YOLO('yolov8n.pt')
yolo_class_names = model.names

def dectect_elements(image):
    results = model(image)
    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            print(box.xyxy[0].astype(int)) 
            print(box.data[0][5].astype(int)) 


if __name__ == '__main__':
    image_path = 'frames/frame_19700101053001.jpg' # Temporarily hard-coded
    # image_path = '/tmp/pexels-markus-spiske-112784.jpg'
    dectect_elements(image_path)