from queue import Queue
import requests
from bs4 import BeautifulSoup
import re
import boto3
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
}
MAIN_URL = "http://www.adaderana.lk/"
QUERY_URL = "http://www.adaderana.lk/search_results.php?mode=2&show=1&query="
SQS_URL = os.environ["SQS_URL"]


def lambda_handler(event, context):
    page = requests.get(
        QUERY_URL + event["query"],
        headers=HEADERS,
    )
    # page = requests.get(context.URL, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")

    news_cards = soup.find_all("div", attrs={"class": "news-story"})

    temp_url_list = []

    for data in news_cards:

        url = data.find_all(href=True)

        temp_url_list.append(url)

    result_list = []

    for i in range(len(temp_url_list) - 1):

        a_tag = str(temp_url_list[i][0])

        clean_tag = a_tag[0:51]
        clean_tag = re.search(r"href=(.*)", clean_tag, re.DOTALL)
        clean_tag = clean_tag.group(1)
        clean_tag = clean_tag.replace('"', "")
        final_url = clean_tag.replace(">", "")

        result_list.append(final_url)

    final_list = []

    client = boto3.client("sqs")

    for item in result_list:
        url = MAIN_URL + item
        final_list.append(url)
        # client.send_message(
        #     QueueUrl=SQS_URL,
        #     MessageBody=url,
        # )

    # response = f"Added {len(final_list)} urls"
    response = {
        "urls": final_list,
    }
    return response
