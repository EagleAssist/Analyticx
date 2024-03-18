from flask import Flask, request, jsonify
from yolo import dectect_elements
import pika  # RabbitMQ

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def detect():
    image = request.files['image']
    image_path = '/tmp/image.jpg'
    image.save(image_path)
    return dectect_elements(image_path)


def connect_and_listen():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name) 

    channel.basic_consume(queue=queue_name, 
                          on_message_callback=process_message, 
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
