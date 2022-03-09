## find search button, assign to object 
## allow user to give parametes for search
## returns list of urls, going page by page 
## gather all urls, exhaust search results 
## with list of urls, visit 1 by 1 to extract info from article + other relevant metadata
## output into a csv 

# class AdaDeranaScraper(object):
#     """[Scraper script for Ada Derana as of 26/2/2022]

    
#     Args:
#         object ([type]): [description]
#     """

import re
from typing import Callable

import pandas as pd
from alive_progress import alive_it
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def __init__(self,query):
    
    self.query = query
    self.base_url = 'http://www.adaderana.lk/'
    self.driver = webdriver.Remote(
            "http://selenium_grid:4444",
            DesiredCapabilities.CHROME,
        )

## navigation functions         
def load_derana(self):

    self.driver.get(self.base_url)
    
def get_search_btns(self):
    
    self.search_box = self.driver.find_element(
        by=By.CSS_SELECTOR, value='div[class="wr-search]')
    
def search_derana(self):
    
    ## send query to search box 
    
    ## return key   
    pass 

def navigate_results(self):
    
    ## from current page 
    ## find the boxes of each article result
    ## check number 
    ## extract url 
    ## click next page
    ## repeat extract till end of pages 
    pass 

## scraper functions below 
    
def get_page_source(self):
    source = self.driver.page_source
    return BeautifulSoup(source, "html.parser")

def make_soup(self):
    self.soup = self.get_page_source()
    self.page = self.driver.page_source
    self.tree = html.fromstring(self.page)

    return self.soup, self.page, self.tree
