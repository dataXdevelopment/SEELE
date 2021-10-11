## MetaCritic Scraper

# import standard libs

import numpy as np
import pandas as pd
import time
import re
from alive_progress import alive_bar

# import scraping libs

from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.parse
from lxml import html
from selenium.webdriver.chrome.options import Options

###


class MetaCriticSraperTool(object):
    '''
    
    
    '''
    def __init__(self, url):

        self.url = url

        self.chrome_options = Options()

        self.chrome_options.add_argument("--headless")

        #self.chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

        self.driver = webdriver.Chrome('./chromedriver',
                                       chrome_options=self.chrome_options)

    def load_website(self, url):

        ## get user input for url to scrape

        # url = input("Enter the MetaCritic page you wish to scrape:")

        self.driver.get(url)

        ## driver.get('https://www.metacritic.com/game/pc/dota-2/user-reviews?sort-by=date&num_items=100')

        ## display product name

        product_title = self.driver.find_element_by_css_selector(
            'div[class="product_title"]').text

        yield print(f'Site loaded for product : {product_title}')

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
        '''
        BeautifulSoup for extracting elements 
        '''

        self.main_list = []

        self.review_cards = self.soup.find_all(
            "div", attrs={"class": 'review_content'})

        for review in self.review_cards:

            temp_list = []

            date = review.find("div", attrs={"class": "date"}).text

            rating = review.find("div", attrs={"class": "review_grade"}).text

            review = review.find("div", attrs={"class": "review_body"}).text

            try:
                user = review.find("div", attrs={"class": "name"}).text

            except:
                user = 'Anonymous'

            temp_list.append(user)
            temp_list.append(date)
            temp_list.append(rating)
            temp_list.append(review)

            self.main_list.append(temp_list)

        return self.main_list

    def get_no_pages(self):
        '''
        Gets the numbers of pages for the product to figure out pagination range
        '''

        product_title = self.driver.find_element_by_css_selector(
            'div[class="product_title"]').text

        number_of_pages = self.driver.find_element_by_css_selector(
            'li[class="page last_page"]').text

        number_of_pages = re.findall(r'\d+', number_of_pages)

        page_count = int(number_of_pages[0])

        num_reviews = 100 * page_count

        yield print(
            f"{product_title} has {page_count} pages of reviews. \nThat's approximately {num_reviews} reviews!"
        )

        return page_count

    # ## Section 2: Main scraping function

    def main_scraper(self, url):
        '''
        Scrapes each page using BS4 and paginates till end
        '''

        self.load_website(url)

        self.reviews = []

        page_count = self.get_no_pages()

        current_page = 0

        with alive_bar(100) as bar:
            for i in range(page_count):

                self.get_page_source()

                self.soup, self.page, self.tree = self.make_soup()

                reviews_in_page = self.extract_reviews_from_page()

                for element in reviews_in_page:

                    self.reviews.append(element)

                current_page += 1

                bar()

                ## note to devinda - progress bar above, text update below? how to send concurrently

                yield print(
                    f'Page {current_page} complete. Moving onto next page ...')

                self.click_next()

            #print(type(self.reviews))

            # print(self.reviews[1][1])

            return self.reviews

    def make_dataframe(self):

        self.df = pd.DataFrame(self.reviews)

        self.df.columns = ['user', 'date', 'rating', 'review']

        return self.df

    def clean_ratings(self):

        yield print('Cleaning ratings ...')

        ls = []

        ls2 = []

        for index, row in self.df.iterrows():
            ls.append(row['rating'])

        for rating in ls:
            final_numerical_rating = re.findall(r'\d+', rating)
            ls2.append(int(final_numerical_rating[0]))

        self.df['rating'] = ls2

        return self.df

    def clean_review(self):

        yield print('Cleaning reviews ...')

        ls = []

        ls2 = []

        for index, row in self.df.iterrows():
            ls.append(row['review'])

        for review in ls:

            clean_review = review.replace('\n', '')
            ls2.append(clean_review)

        self.df['review'] = ls2

        return self.df

    def is_english(self, string):
        '''
        Determine if string is English or not
        '''

        try:
            string.encode(encoding='utf-8').decode('ascii')

        except UnicodeDecodeError:
            return False

        else:
            return True

    def remove_foreign_langs(self):
        '''
        Iterates through dataframe to drop all non-English rows
        '''

        yield print('Removing all non-English reviews ...')

        for index, row in self.df.iterrows():

            test = self.is_english(row['review'])

            if test == False:

                self.df.drop(index, inplace=True)

            else:
                pass

        return self.df

    def save_file_and_exit(self):

        # product_name = driver.find_element_by_css_selector('div[class="product_title"]').text

        # product = product_name()

        # print('File saved ... Now exiting ...')

        # exit()

        csv_out = self.df.to_csv('MetacriticReviews_.csv')

        return csv_out

    def run_scraper(self, url):

        # product_name = product_name(driver)

        #load_website(url)

        all_reviews = self.main_scraper(url)

        # final_list = []

        # for page_of_reviews in all_reviews:
        #     for review in page_of_reviews:
        #         final_list.append(review)

        self.driver.close()

        df = self.make_dataframe()

        cleaned_1 = self.clean_ratings()

        cleaned_2 = self.clean_review()

        clean = self.remove_foreign_langs()

        return self.save_file_and_exit()


if __name__ == "__main__":

    pass
