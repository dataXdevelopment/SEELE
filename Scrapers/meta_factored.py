"""
This module exports the MetaCriticScaperTool class which allows
for the generation of a csv for a given MetaCritic Url
"""

import re
from typing import Callable

import pandas as pd
from alive_progress import alive_it
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Defines default output folder name
output_folder = "output"


class MetaCriticScraper(object):
    """Generated a CSV for a given MetaCritic Url
    instance.run_scraper returns the CSV file
    Args:
        url (string): Valid MetaCritic Url
    """

    def __init__(self, url, status_updater: Callable[[int], None]):
        self.url = url
        self.driver = webdriver.Remote(
            "http://selenium_grid:4444",
            DesiredCapabilities.CHROME,
        )
        self.product_title = ""
        self.status_updater = status_updater

    def load_website(self):
        self.driver.get(self.url)
        self.product_title = self.driver.find_element(
            by=By.CSS_SELECTOR, value='div[class="product_title"]').text

        print(f"Site loaded for product : {self.product_title}")

    def click_next(self):
        self.driver.find_element(by=By.CSS_SELECTOR,
                                 value='span[class="flipper next"]').click()

    def get_page_source(self):
        source = self.driver.page_source
        return BeautifulSoup(source, "html.parser")

    def make_soup(self):
        self.soup = self.get_page_source()
        self.page = self.driver.page_source
        self.tree = html.fromstring(self.page)

        return self.soup, self.page, self.tree

    def extract_reviews_from_page(self):
        self.main_list = []
        self.review_cards = self.soup.find_all(
            "div", attrs={"class": "review_content"})

        for review in self.review_cards:
            temp_list = []

            date = review.find("div", attrs={"class": "date"}).text
            rating = review.find("div", attrs={"class": "review_grade"}).text
            review_body = review.find("div", attrs={
                "class": "review_body"
            }).text

            try:
                user = review.find("div", attrs={"class": "name"}).text
            except AttributeError:  # pylint: disable=bare-except
                user = "Anonymous"

            name = user.strip()
            review_text = str(review_body).strip()

            temp_list.append(name)
            temp_list.append(date)
            temp_list.append(rating)
            temp_list.append(review_text)

            self.main_list.append(temp_list)

        return self.main_list

    def get_no_pages(self):
        product_title = self.driver.find_element(
            by=By.CSS_SELECTOR, value='div[class="product_title"]').text
        number_of_pages = self.driver.find_element(
            by=By.CSS_SELECTOR, value='li[class="page last_page"]').text
        number_of_pages = re.findall(r"\d+", number_of_pages)
        page_count = int(number_of_pages[0])
        num_reviews = 100 * page_count

        print(f"{product_title} has {page_count} pages of reviews."
              f"That's approximately {num_reviews} reviews!")

        return page_count

    def main_scraper(self):
        self.reviews = []
        current_page = 0

        self.load_website()
        # page_count = self.get_no_pages()
        page_count = 5

        for _ in alive_it(range(page_count)):
            self.get_page_source()
            self.soup, self.page, self.tree = self.make_soup()
            reviews_in_page = self.extract_reviews_from_page()

            for element in reviews_in_page:
                self.reviews.append(element)

            current_page += 1
            print(f"Page {current_page} complete. Moving onto next page ...")

            self.click_next()
            self.status_updater(current_page / page_count * 100)

    def make_dataframe(self):
        self.df = pd.DataFrame(self.reviews)
        self.df.columns = ["user", "date", "rating", "review"]

        return self.df

    def clean_ratings(self):
        print("Cleaning ratings ...")

        ls = []
        ls2 = []

        for _, row in self.df.iterrows():
            ls.append(row["rating"])

        for rating in ls:
            final_numerical_rating = re.findall(r"\d+", rating)
            ls2.append(int(final_numerical_rating[0]))

        self.df["rating"] = ls2

        return self.df

    def clean_review(self):
        print("Cleaning reviews ...")

        ls = []
        ls2 = []

        for _, row in self.df.iterrows():
            ls.append(row["review"])

        for review in ls:
            clean_review = review.replace("\n", "")
            ls2.append(clean_review)

        self.df["review"] = ls2

        return self.df

    def is_english(self, string):
        try:
            string.encode(encoding="utf-8").decode("ascii")
        except UnicodeDecodeError:
            return False
        else:
            return True

    def remove_foreign_langs(self):
        """
        Iterates through dataframe to drop all non-English rows
        """
        print("Removing all non-English reviews ...")

        for index, row in self.df.iterrows():
            test = self.is_english(row["review"])
            if test is False:
                self.df.drop(index, inplace=True)
            else:
                pass

        return self.df

    def to_csv(self) -> str:
        """
            Converts the df to a csv and returns the filename
        Returns:
            str: Returns the file name of the csv
        """

        title = self.product_title.replace(" ", "_").lower()
        file_name = f"{title}_metacritic_user_reviews.csv"
        self.df.to_csv(f"{output_folder}/{file_name}", index=False)

        print(f"{file_name} saved!")
        return file_name

    def upload_csv():
        return True

    def run(self):
        print("Scraping MetaCritic ...")

        self.main_scraper()
        self.driver.quit()
        self.make_dataframe()
        self.clean_ratings()
        self.clean_review()
        self.remove_foreign_langs()
        return True


if __name__ == "__main__":
    import sys
    from pathlib import Path

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    url = sys.argv[1]
    chrome_driver = sys.argv[2]

    scraper = MetaCriticScraper(url, chrome_driver)
    scraper.run()
    scraper.to_csv()
