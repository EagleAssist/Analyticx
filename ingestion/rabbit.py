import pika


def push_to_queue(frame_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq')) # TODO : Optimize this part, Maybe use a singleton connection
    channel = connection.channel()
    channel.queue_declare(queue='raw-frames')
    channel.basic_publish(exchange='',
                          routing_key='raw-frames',
                          body=frame_path) # TODO : Add video_id to the payload
    connection.close()
