import json
import os
import random
import sys
from time import sleep

import pika
from dotenv import dotenv_values
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

config = dotenv_values(".env")

transport = AIOHTTPTransport(url=config["DAGON_GRAPHQL_URL"],
                             headers={'x-api-key': config["WORKER_API_KEY"]})
with open(os.path.join(os.path.dirname(__file__), "schema.graphql")) as f:
    schema_str = f.read()

client = Client(transport=transport, schema=schema_str)


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
        updateStatus(task_id, "RUNNING")

        print("Processing Task " + str(task_id))

        sleep(random.randint(10, 30))

        download_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
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
