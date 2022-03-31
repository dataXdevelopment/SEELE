import json
import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import boto3


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
}
MAIN_URL = "http://www.adaderana.lk/"
QUERY_URL = "http://www.adaderana.lk/search_results.php?mode=2&show=1&query="


def split(list_a, chunk_size):
    for i in range(0, len(list_a), chunk_size):
        yield list_a[i : i + chunk_size]


def search(queryTerm):
    page = requests.get(
        QUERY_URL + queryTerm,
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

    for item in result_list:
        url = MAIN_URL + item
        final_list.append(url)

    splitSize = int(os.environ["SPLIT_SIZE"])
    response = list(split(final_list, splitSize))
    return response


def insert_into_dynamodb(urlCollectionList, job_id):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("query_to_scrape")

    for index, urlCollection in enumerate(urlCollectionList):
        record = {
            "job_id": job_id,
            "index": str(index),
            "urls": set(urlCollection),
        }
        print(record)
        table.put_item(Item=record)

    print("Inserted into dynamodb")


def send_task_success(result):
    client = boto3.client("stepfunctions")
    indexes = list(range(0, len(result)))
    response = client.send_task_success(
        taskToken=os.environ["TASK_TOKEN_ENV_VARIABLE"],
        output=json.dumps(indexes),
    )
    print(response)


def main():
    queryTerm = sys.argv[1]
    job_id = sys.argv[2]

    result = search(queryTerm)
    print(result)

    insert_into_dynamodb(result, job_id)
    send_task_success(result)


if __name__ == "__main__":
    main()
