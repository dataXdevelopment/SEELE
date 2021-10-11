"""
This module exports the MetaCriticScaperTool class which allows
for the generation of a csv for a given MetaCritic Url
"""

import pandas as pd
import time
import re
from alive_progress import alive_it

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from lxml import html


class MetaCriticSraperTool(object



        ):
  """Generated a CSV for a given MetaCritic Url

  instance.run_scraper returns the CSV file

  Args:
      url (string): Valid MetaCritic Url
  """

  def __init__(self, url):

    self.url = url

    self.chrome_options = Options()

    self.chrome_options.add_argument("--headless")

    # self.chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'   #pylint: disable=line-too-long

    self.driver = webdriver.Chrome("./chromedriver",
                                   chrome_options=self.chrome_options)

  def load_website(self, url):

    ## get user input for url to scrape

    # url = input("Enter the MetaCritic page you wish to scrape:")

    self.driver.get(url)

    ## driver.get('https://www.metacritic.com/game/pc/dota-2/user-reviews?sort-by=date&num_items=100') #pylint: disable=line-too-long

    ## display product name

    product_title = self.driver.find_element_by_css_selector(
        'div[class="product_title"]').text

    yield print(f"Site loaded for product : {product_title}")

    # sleep to ensure page is loaded correctly

    time.sleep(5)

  def click_next(self):

    self.driver.find_element_by_css_selector(
        'span[class="flipper next"]').click()

  def get_page_source(self):

    source = self.driver.page_source

    return BeautifulSoup(source, "html.parser")

  def make_soup(self):

    self.soup = self.get_page_source()
    self.page = self.driver.page_source
    self.tree = html.fromstring(self.page)

    return self.soup, self.page, self.tree

  def extract_reviews_from_page(self):
    """
        BeautifulSoup for extracting elements
        """

    self.main_list = []

    self.review_cards = self.soup.find_all("div",
                                           attrs={"class": "review_content"})

    for review in self.review_cards:

      temp_list = []

      date = review.find("div", attrs={"class": "date"}).text

      rating = review.find("div", attrs={"class": "review_grade"}).text

      review = review.find("div", attrs={"class": "review_body"}).text

      try:
        user = review.find("div", attrs={"class": "name"}).text
      #FIXME Find correct error
      except:  #pylint: disable=bare-except
        user = "Anonymous"

      temp_list.append(user)
      temp_list.append(date)
      temp_list.append(rating)
      temp_list.append(review)

      self.main_list.append(temp_list)

    return self.main_list

  def get_no_pages(self):
    """
        Gets the numbers of pages for the product to figure out pagination range
        """

    product_title = self.driver.find_element_by_css_selector(
        'div[class="product_title"]').text

    number_of_pages = self.driver.find_element_by_css_selector(
        'li[class="page last_page"]').text

    number_of_pages = re.findall(r"\d+", number_of_pages)

    page_count = int(number_of_pages[0])

    num_reviews = 100 * page_count

    yield print(f"{product_title} has {page_count} pages of reviews."
                f"That's approximately {num_reviews} reviews!")

    return page_count

  # ## Section 2: Main scraping function

  def main_scraper(self, url):
    """
        Scrapes each page using BS4 and paginates till end
        """

    self.load_website(url)

    self.reviews = []

    page_count = self.get_no_pages()

    current_page = 0

    for _ in alive_it(range(page_count)):

      self.get_page_source()

      self.soup, self.page, self.tree = self.make_soup()

      reviews_in_page = self.extract_reviews_from_page()

      for element in reviews_in_page:

        self.reviews.append(element)

      current_page += 1
      ## note to devinda - progress bar above, text update below? how to send concurrently #pylint: disable=line-too-long

      yield print(f"Page {current_page} complete. Moving onto next page ...")

      self.click_next()

    # print(type(self.reviews))

    # print(self.reviews[1][1])

    return self.reviews

  def make_dataframe(self):

    self.df = pd.DataFrame(self.reviews)

    self.df.columns = ["user", "date", "rating", "review"]

    return self.df

  def clean_ratings(self):

    yield print("Cleaning ratings ...")

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

    yield print("Cleaning reviews ...")

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
    """
        Determine if string is English or not
        """

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

    yield print("Removing all non-English reviews ...")

    for index, row in self.df.iterrows():

      test = self.is_english(row["review"])

      if test is False:

        self.df.drop(index, inplace=True)

      else:
        pass

    return self.df

  def save_file_and_exit(self):

    # product_name = driver.find_element_by_css_selector('div[class="product_title"]').text #pylint: disable=line-too-long

    # product = product_name()

    # print('File saved ... Now exiting ...')

    # exit()

    csv_out = self.df.to_csv("MetacriticReviews_.csv")

    return csv_out

  def run_scraper(self, url):

    # product_name = product_name(driver)

    # load_website(url)

    self.main_scraper(url)

    self.driver.close()

    self.make_dataframe()

    self.clean_ratings()

    self.clean_review()

    self.remove_foreign_langs()

    return self.save_file_and_exit()


if __name__ == "__main__":

  pass
