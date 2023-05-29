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
    wait = WebDriverWait(browser, 10)
    links = []

    for page in range(1, pagesToGet + 1):
        url = "https://nypost.com/search/%s/page/%d/?orderby=relevance" % (keyword, page)
        #an exception might be thrown, so the code should be in a try-except block
        try:
            #use the browser to get the url. This is suspicious command that might blow up.
            browser.get(url)
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//div[contains(concat(' ', @class, ' '), ' search-results__story ')]//h3[contains(concat(' ', @class, ' '), ' story__headline ')]/a[@href]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except Exception as e:
            warnings.warn("Stuck attempting to get page %d, skipping..." % page)
            break
    return links

# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/nypost_links.csv', index=False)

def getContent(links):
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    contents = []

    for link in links:
        try:
            browser.get(link)
            # Get headline and description
            headline_el = wait.until(lambda d: d.find_element(By.XPATH, "//meta[@name='sailthru.title']"))
            headline = headline_el.get_attribute("content")
            description_el = browser.find_element(By.XPATH, "//meta[@name='sailthru.description']")
            description = description_el.get_attribute("content")
            # Get article body
            elems = browser.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' entry-content ')]/p")
            articleBody = ' '.join([elem.text for elem in elems])
            contents.append({'Headline': headline, 'Description': description, 'Content': articleBody})
        except:
            error_type, _, error_info = sys.exc_info()
            warnings.warn('ERROR FOR LINK: %s' % str(link))
            warnings.warn('%s\nLine: %s' % (str(error_type), str(error_info.tb_lineno)))
            continue

    return contents

df = pd.read_csv('data/nypost_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/nypost_contents.csv', index=False)