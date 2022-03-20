import requests
from bs4 import BeautifulSoup


class DeranaScraper:
    def __init__(self, query):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
        }
        self.query = query
        self.search_base_url = (
            "http://www.adaderana.lk/search_results.php?mode=2&show=1&query="
        )
        self.main_url = "http://www.adaderana.lk/"
        self.url = self.base_string + self.test_query

    def scrape_urls(self):

        page = requests.get(self.URL, headers=self.headers)
        soup = BeautifulSoup(page.content, "html.parser")

        news_cards = soup.find_all("div", attrs={"class": "news-story"})

        temp_url_list = []

        for data in news_cards:

            url = data.find_all(href=True)

            temp_url_list.append(url)

        result_list = []

        for i in range(len(temp_url_list)):

            a_tag = str(temp_url_list[i][0])

            clean_tag = a_tag[0:51]
            clean_tag = re.search(r"href=(.*)", clean_tag, re.DOTALL)
            clean_tag = clean_tag.group(1)
            clean_tag = clean_tag.replace('"', "")
            final_url = clean_tag.replace(">", "")

            result_list.append(final_url)

        self.final_list = []

        for item in result_list:
            url = self.main_url + item
            self.final_list.append(url)

        return self.final_list

    def scrape_pages(self):

        database = []

        i = 0

        for url in final_list:

            record = []
            print(url)

            page = requests.get(url, headers=headers)
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

            database.append(record)
            i += 1
            print("Record " + str(i) + " complete ...")

            time.sleep(5)

        self.df = pd.DataFrame(database, columns=["ArticleTitle", "Date", "Body"])

        return self.df
