import datetime
import json
import os
import sys

import pika
from dotenv import dotenv_values
from google.cloud import storage
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from Scrapers.meta_factored import MetaCriticScraper


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


def updateStatus(id, status, result=None):
    print(f"Status: {status}")
    query = gql("""
            mutation UpdateTaskMutation($id: Int!, $input: UpdateTaskInput!) {
                updateTask(id: $id, input: $input) {
                    id
                    status
                }
            }
        """)

    queryInput = {
        "status": status,
    }
    if (result):
        queryInput["result"] = result

    params = {"id": id, "input": queryInput}
    result = client.execute(query, variable_values=params)
    print(result)


config = dotenv_values(".env")

transport = AIOHTTPTransport(url=config["DAGON_GRAPHQL_URL"],
                             headers={'x-api-key': config["WORKER_API_KEY"]})
with open(os.path.join(os.path.dirname(__file__), "schema.graphql")) as f:
    schema_str = f.read()

client = Client(transport=transport, schema=schema_str)


def main():
    queue_name = config["QUEUE_NAME"]
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config["AMPQ_URL"]))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        print("Started Task")

        request = json.loads(body)
        task_id = request['id']

        print("Processing Task")
        updateStatus(task_id, "RUNNING")

        task_url = request['name']
        scraper = MetaCriticScraper(task_url)
        scraper.run()
        output_file = scraper.to_csv()

        download_url = upload_to_gcs(output_file)
        updateStatus(task_id, "COMPLETED", download_url)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print("Task Completed")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

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
