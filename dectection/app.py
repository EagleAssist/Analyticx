from flask import Flask, request, jsonify
from app import dectect_elements

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def detect():
    image = request.files['image']
    image_path = '/tmp/image.jpg'
    image.save(image_path)
    return dectect_elements(image_path)

@app.route('/')
def index():
    return 'Dectection Module of YOLO'

@app.route('/health')
def health():
    return 'YOLO-Dectection Landscape is  Healthy'