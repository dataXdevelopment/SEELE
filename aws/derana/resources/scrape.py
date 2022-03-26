import requests
from bs4 import BeautifulSoup
import boto3
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
}


def scrape(url, job_id):
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")

    try:
        name = soup.find("h1").text
        date = soup.find("p", attrs={"class": "news-datestamp"}).text.strip()
        body = soup.find("div", attrs={"class": "news-content"}).text.strip()
    except:
        print("An element was not found")

    print("Record complete ...")

    response = {
        "url": url,
        "job_id": job_id,
        "engine": "ada_derana",
        "data": {
            "name": name,
            "date": date,
            "body": body,
        },
    }

    return response


def insert_into_dynamodb(record):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("scrape_results")
    table.put_item(Item=record)


def main():
    job_id = sys.argv[2]
    url = sys.argv[1] or "http://www.adaderana.lk/news.php?nid=81417"
    result = scrape(url, job_id)
    insert_into_dynamodb(result)
    print(result)


if __name__ == "__main__":
    main()
