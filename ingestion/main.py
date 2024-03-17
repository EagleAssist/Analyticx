from flask import Flask, render_template, request, redirect
import cv2
import os
from minio import Minio
from datetime import datetime
from minio.error import S3Error
from dotenv  import load_dotenv


load_dotenv()

minio_client = {
    Minio("minio:9000",
          access_key=os.getenv('MINIO_ACCESS_KEY'),
          secret_key=os.getenv('MINIO_SECRET_KEY'),
          secure=False)
}

app = Flask(__name__)

# Create 'uploads' and 'frames' directories if they don't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if not os.path.exists('frames'):
    os.makedirs('frames')


def save_frame(image, frame_path):
    try:
        cv2.imwrite(frame_path, image)
        source_file = frame_path
        bucket_name = "storageone"
        destination_file = frame_path

        # TODO : upload these files in another file and diffrent thread
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)
            print("Created bucket", bucket_name)
        else:
            print("Bucket", bucket_name, "already exists")
        
        print("Uploading", source_file, "as", destination_file, "to bucket", bucket_name, "...")
        minio_client.fput_object(
        bucket_name, destination_file, source_file,
        )
        print(source_file, "successfully uploaded as object", destination_file, "to bucket", bucket_name,
        )
    except Exception as e:
        print(f'Error sending the frame: {e}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        # return redirect(request.url) # TODO: Add error message
        render_template('error.html', error_type='file_not_found')

    file = request.files['file']
    
    if file.filename == '':
        # return redirect(request.url) # TODO: Add error message
        render_template('error.html',error_type="empty_filename")

    if file:
        video_path = os.path.join('uploads', file.filename)
        file.save(video_path)

        vidcap = cv2.VideoCapture(video_path)
        fps = vidcap.get(cv2.CAP_PROP_FPS)  # Get frames per second
        frames_per_second = 1 / 12  # Set the desired frames every 12 seconds
        frame_interval = int(round(fps / frames_per_second))
        success, image = vidcap.read()
        count = 0

        while success:
            if count % frame_interval == 0:
                timestamp = vidcap.get(cv2.CAP_PROP_POS_MSEC) // 1000  # Get timestamp in seconds
                hours = int(timestamp // 3600)  # Calculate hours
                minutes = int((timestamp % 3600) // 60)  # Calculate minutes
                seconds = int(timestamp % 60)  # Calculate seconds

                frame_path = os.path.join('frames', f'frame{hours}h-{minutes}m-{seconds}s.jpg')
                os.makedirs(os.path.dirname(frame_path), exist_ok=True)  # Ensure subdirectories exist
                
                save_frame(image, frame_path)


            success, image = vidcap.read()
            count += 1

        return render_template('result.html', count=count)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')