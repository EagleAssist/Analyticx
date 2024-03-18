from flask import Flask, request, jsonify
from yolo import dectect_elements
import pika  # RabbitMQ

app = Flask(__name__)


# TODO : Move this to a separate file
def fetch_from_minio(frame_path):
    # TODO : Fetch from Minio
    pass

@app.route('/detect', methods=['POST'])
def detect():
    image = request.files['image']
    image_path = '/tmp/image.jpg'
    image.save(image_path)
    return dectect_elements(image_path)


def process_message(ch, method, properties, body):
    print(f' [x] Received {body}')
    # TODO : Fetch from Minio and respond to dectect elements use f_get_object
    fetch_from_minio(body)
    dectect_elements(body)
    print(f' [x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)

def connect_and_listen():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    # channel.queue_declare(queue=queue_name) Should be declared in the ingestion module 

    channel.basic_consume(queue='raw-frames', 
                          on_message_callback=process_message, # which process to perform
                          auto_ack=True)  # Acknowledge messages automatically

    try:
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()



@app.route('/')
def index():
    return 'Dectection Module of YOLO'

@app.route('/health')
def health():
    return 'YOLO-Dectection Landscape is Healthy'

connect_and_listen()  # Consider using a Thread for this
app.run(debug=True) 
