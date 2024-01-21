from flask import Flask, render_template, request, redirect
import cv2
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        video_path = os.path.join('uploads', file.filename)
        file.save(video_path)

        vidcap = cv2.VideoCapture(video_path)
        fps = vidcap.get(cv2.CAP_PROP_FPS)  # Get frames per second
        frames_per_second = 2  # Set the desired frames per second
        frame_interval = int(round(fps / frames_per_second))
        success, image = vidcap.read()
        count = 0

        while success:
            if count % frame_interval == 0:
                timestamp = vidcap.get(cv2.CAP_PROP_POS_MSEC) // 1000  # Get timestamp in seconds
                time_str = datetime.fromtimestamp(timestamp).strftime('%Y%m%d%H%M%S')
                frame_path = os.path.join('frames', f'frame_{time_str}.jpg')
                cv2.imwrite(frame_path, image)
            success, image = vidcap.read()
            count += 1

        return render_template('result.html', count=count)

if __name__ == '__main__':
    app.run(debug=True)