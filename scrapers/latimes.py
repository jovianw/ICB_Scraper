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
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line
warnings.simplefilter('always', UserWarning)

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1:
        warnings.warn("Can't get less than 1 pages")
        return []
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    links = []

    for page in range(1, pagesToGet + 1):
        url = f"https://www.latimes.com/search?q={keyword}&f1=0000016a-ea2d-db5d-a57f-fb2dc8680000&s=0&p={page}"
        #an exception might be thrown, so the code should be in a try-except block
        try:
            #use the browser to get the url. This is suspicious command that might blow up.
            browser.get(url)
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//ul[@class='search-results-module-results-menu']/li//div[contains(concat(' ', @class, ' '), ' promo-media ')]/a[@href]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except Exception as e:
            warnings.warn("Stuck attempting to get page %d, skipping..." % page)
            break
    return links


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/latimes_links.csv', index=False)


def getContent(links):
    browser = webdriver.Chrome()
    contents = []

    for link in links:
        try:
            browser.get(link)
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            parsed_el = json.loads(el.get_attribute("innerHTML"))
            contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el.get('articleBody')})
        except Exception as err:
            warnings.warn(f"{type(err)}: {err}")
            warnings.warn('ERROR FOR LINK:', link)
            continue

    return contents

df = pd.read_csv('data/latimes_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/latimes_contents.csv', index=False)