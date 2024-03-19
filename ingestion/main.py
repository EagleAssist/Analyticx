from flask import Flask, render_template, request, redirect
import cv2
import os
from minio import Minio
from datetime import datetime
from minio.error import S3Error
from dotenv  import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from utils import Calculate_hash
from rabbit import push_to_queue

load_dotenv()

# Insecure : Hardoded credentials as its local only
minio_client = Minio("minio:9000",
                     access_key="O22u8yhKEhqOFGKu",
                     secret_key="Chd5l7J3VWWuJ9V17KxJgJi4Wdr24tW0",
                     secure=False)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://username:password@postgres:5432/main"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# TODO : Move these to Models.py
class Videos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    hash = db.Column(db.String(300), nullable=True)
    length = db.Column(db.Integer, nullable=False)
    frames = db.Column(db.Integer, nullable=False)

class Frames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    frame_path = db.Column(db.String(1000), nullable=False) # Minio Path
    processed = db.Column(db.Boolean, default=False)
    text = db.Column(db.String(10000), nullable=True) 

    def __repr__(self):
        return '<Video %r>' % self.id


with app.app_context():   # Ensures proper context
    print("Creating tables...")
    db.create_all()
    print("Tables created")


# Create 'uploads' and 'frames' directories if they don't exist
# TODO : Replace frames with minio
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if not os.path.exists('frames'):
    os.makedirs('frames')


def save_frame(image, frame_path):
    try:
        cv2.imwrite(frame_path, image)

        # source_file = frame_path
        # bucket_name = "storageone"
        # destination_file = frame_path

        # # TODO : upload these files in another file and diffrent thread
        # found = minio_client.bucket_exists(bucket_name)
        # if not found:
        #     minio_client.make_bucket(bucket_name)
        #     print("Created bucket", bucket_name)
        # else:
        #     print("Bucket", bucket_name, "already exists")
        
        # print("Uploading", source_file, "as", destination_file, "to bucket", bucket_name, "...")
        # minio_client.fput_object(
        # bucket_name, destination_file, source_file,
        # )
        # print(source_file, "successfully uploaded as object", destination_file, "to bucket", bucket_name,
        # )
        push_to_queue(frame_path)
        os.remove(frame_path)

    except Exception as e:
        print(f'Error sending the frame: {e}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    # TODO : Perform checks in another file
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
        hash_value = Calculate_hash(file)
        try:
            db_entry_video = Videos(name=file.filename, hash=hash_value, length=vidcap.get(cv2.CAP_PROP_FRAME_COUNT), frames=0)
            db.session.add(db_entry_video)
            db.session.commit()
        except Exception as e:
            print(f'Error adding video to database: {e}')

        while success:
            if count % frame_interval == 0:
                timestamp = vidcap.get(cv2.CAP_PROP_POS_MSEC) // 1000  # Get timestamp in seconds
                hours = int(timestamp // 3600)  # Calculate hours
                minutes = int((timestamp % 3600) // 60)  # Calculate minutes
                seconds = int(timestamp % 60)  # Calculate seconds

                frame_path = os.path.join('frames', f'frame{hours}h-{minutes}m-{seconds}s.jpg')

                try:
                    db_entry_frame = Frames(video_id=db_entry_video.id, frame_path=frame_path)
                    db.session.add(db_entry_frame)
                    db.session.commit()
                except Exception as e:
                    print(f'Error adding frame data to database: {e}')

                save_frame(image, frame_path)

            success, image = vidcap.read()
            count += 1
            # TODO : Add the no of frames processed into the video DB
        return render_template('result.html', count=count)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')