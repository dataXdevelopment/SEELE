import json
import os
import sys
import time

import pika
import redis
from Scrapers.meta_factored import MetaCriticScraper


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    request_queue = 'tasks.metacritic.requests'
    response_queue = 'tasks.metacritic.responses'
    channel.queue_declare(queue=request_queue, durable=True)
    channel.queue_declare(queue=response_queue, durable=True)
    redis_client = redis.Redis(host='redis',
                               decode_responses=True,
                               charset='utf-8')

    def callback(ch, method, properties, body):
        print("Started Task")
        request = json.loads(body)
        print(request)
        task_id = request['id']
        url = request['task']['url']
        # scraper = MetaCriticScraper(url)
        # scraper.run()
        # scraper.to_csv()
        print(task_id)
        print("Processing Task")
        time.sleep(10)

        response = request
        response['data'] = url
        response['status'] = 'COMPLETED'

        redis_client.set(task_id, json.dumps(response))

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Task Completed")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=request_queue, on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
