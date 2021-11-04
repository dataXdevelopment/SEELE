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
    channel.queue_declare(queue=request_queue, durable=True)
    redis_client = redis.Redis(host='redis',
                               decode_responses=True,
                               charset='utf-8')

    def update_percentage(new_percentage, data):
        task_id = data['scrapeStatus']['id']
        data['scrapeStatus']['percentage'] = new_percentage
        redis_client.publish(f'tasks.metacritic.results.{task_id}',
                             json.dumps(data))

    def complete_percentage(data):
        task_id = data['scrapeStatus']['id']
        data['scrapeStatus']['percentage'] = 100
        data['scrapeStatus']['status'] = 'COMPLETED'
        redis_client.publish(f'tasks.metacritic.results.{task_id}',
                             json.dumps(data))

    def callback(ch, method, properties, body):
        print("Started Task")

        request = json.loads(body)
        task_id = request['id']

        response = request
        print(request)

        response['status'] = 'IN_PROGRESS'
        redis_client.set(task_id, json.dumps(response))

        # url = request['task']['url']
        # scraper = MetaCriticScraper(url)
        # scraper.run()
        # scraper.to_csv()
        data = {}
        data['scrapeStatus'] = response

        print("Processing Task")
        count = 0

        while count < 20:
            count += 1
            update_percentage(new_percentage=count, data=data)
            time.sleep(1)

        response[
            'data'] = "https://pbs.twimg.com/media/FBWBM9MVgAE58S-?format=jpg&name=large"

        complete_percentage(data)
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
