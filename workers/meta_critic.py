import datetime
import json
import os
import sys

import pika
import redis
from Scrapers.meta_factored import MetaCriticScraper
from google.cloud import storage


def upload_to_gcs(output_file) -> str:
    """Uploads to google cloud storage and returns a signed URL to download

    Args:
        output_file ([string]): Name of the file to upload

    Returns:
        str: Signed URL to download the file
    """
    storage_client = storage.Client()

    bucket_name = 'worker_uploads'
    source_file_name = f'./output/{output_file}'
    destination_blob_name = output_file

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    download_url = blob.generate_signed_url(
        version='v4', expiration=datetime.timedelta(minutes=15), method='GET')

    print("File {} uploaded to {} with url {}.".format(source_file_name,
                                                       destination_blob_name,
                                                       download_url))
    return download_url


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    request_queue = 'tasks.metacritic.requests'
    channel.queue_declare(queue=request_queue, durable=True)
    redis_client = redis.Redis(host='redis',
                               decode_responses=True,
                               charset='utf-8')

    def callback(ch, method, properties, body):
        print("Started Task")

        request = json.loads(body)
        task_id = request['id']

        data = {}
        data['scrapeStatus'] = request
        response = data['scrapeStatus']

        def update_percentage(new_percentage):
            response['percentage'] = new_percentage
            redis_client.publish(f'tasks.metacritic.results.{task_id}',
                                 json.dumps(data))

        def complete_percentage():
            response['percentage'] = 100
            response['status'] = 'COMPLETED'
            redis_client.publish(f'tasks.metacritic.results.{task_id}',
                                 json.dumps(data))

        response['status'] = 'IN_PROGRESS'
        redis_client.set(task_id, json.dumps(response))
        print("Processing Task")

        task_url = request['task']['url']
        scraper = MetaCriticScraper(task_url, update_percentage)
        scraper.run()
        output_file = scraper.to_csv()

        download_url = upload_to_gcs(output_file)

        response['data'] = download_url

        complete_percentage()
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
