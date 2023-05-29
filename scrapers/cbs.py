import os
import requests
import json
import warnings
import pandas as pd
import time
import urllib.request,sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

keyword = "walmart"
pagesToGet= 5
def warning_on_one_line(message, category, filename, lineno, line=None):
    return '%s:%s: %s:\n%s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line
warnings.simplefilter('always', UserWarning)

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1:
        raise Exception("Can't get less than 1 pages")
    browser = webdriver.Chrome()
    browser.set_window_size(1920, 1080)
    wait = WebDriverWait(browser, 10)

    # Load twice to get to search
    browser.get("https://www.cbsnews.com/#search-form:")
    browser.get("https://www.cbsnews.com/#search-form:")

    # Search and enter
    searchField = wait.until(lambda d: d.find_element(By.CLASS_NAME, "search-field"))
    searchField.send_keys(keyword)
    searchField.send_keys(Keys.ENTER)

    # Filter by articles
    articleFilter = wait.until(lambda d: d.find_element(By.XPATH, '//input[@id="search-facet--contenttype-news"]/following-sibling::label'))
    articleFilter.click()

    # Wait until results are loaded
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article"))

    # Press load more
    for page in range(2, pagesToGet + 1):
        # Get next page
        try:
            browser.find_element(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//a[@data-name='endindex'][last()]").click()
        except:
            warnings.warn("Stuck attempting to get page %d, skipping..." % page)
            break
        time.sleep(1)

    # Get all results
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))

    return [elem.get_attribute("href") for elem in elems]


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/cbs_links.csv', index=False)


def getContent(links):
    browser = webdriver.Chrome()
    contents = []

    for link in links:
        try:
            browser.get(link)
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            parsed_el = json.loads(el.get_attribute("innerHTML"))
            contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el['articleBody']})
        except:
            error_type, error_obj, error_info = sys.exc_info()
            warnings.warn('ERROR FOR LINK:', link)
            warnings.warn(error_type, 'Line:', error_info.tb_lineno)
            continue

    return contents

df = pd.read_csv('data/cbs_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/cbs_contents.csv', index=False)