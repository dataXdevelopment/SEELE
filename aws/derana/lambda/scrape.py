import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
}


def lambda_handler(event, context):
    url = event["url"]
    record = []
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")

    try:
        name = soup.find("h1").text
        date = soup.find("p", attrs={"class": "news-datestamp"}).text.strip()
        body = soup.find("div", attrs={"class": "news-content"}).text.strip()
    except:
        print("An element was not found")

    record.append(name)
    record.append(date)
    record.append(body)

    print("Record complete ...")

    df = pd.DataFrame(record, columns=["ArticleTitle", "Date", "Body"])

    return df
