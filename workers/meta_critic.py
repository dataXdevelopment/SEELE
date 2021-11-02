import os
import sys

import pika
import json

from Scrapers.meta_factored import MetaCriticScraper


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='tasks.metacritic', durable=True)

    def callback(ch, method, properties, body):
        # print(" [x] Received %r" % body)
        request = json.loads(body)
        url = request['task']['url']
        scraper = MetaCriticScraper(url)
        scraper.run()
        scraper.to_csv()

    channel.basic_consume(queue='tasks.metacritic',
                          auto_ack=True,
                          on_message_callback=callback)

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
