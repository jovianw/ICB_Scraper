
import urllib.request,sys,time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json

keyword = "Walmart"
pagesToGet= 10

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1:
        raise Exception("Can't get less than 1 pages")
    links = []
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)

    url = 'https://www.washingtonpost.com/search/?query=%s&time=all&sort=relevancy' % keyword
    browser.get(url)

    # Wait until results are loaded
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article[contains(concat(' ',normalize-space(@class),' '),' single-result ')]//a[@href and contains(concat(' ',normalize-space(@class),' '),'font-md')]"))

    # Press load more
    for page in range(2, pagesToGet + 1):
        # Get next page
        browser.find_element(By.XPATH, "//button[.='Load more results']").click()
        time.sleep(1)

    elems = browser.find_elements(By.XPATH, "//article[contains(concat(' ',normalize-space(@class),' '),' single-result ')]//a[@href and contains(concat(' ',normalize-space(@class),' '),'font-md')]")
    return [elem.get_attribute("href") for elem in elems]


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/washingtonpost_links.csv', index=False)


def getContent(links):
    browser = webdriver.Chrome()
    contents = []

    for link in links:
        try:
            browser.get(link)
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            parsed_el = json.loads(el.get_attribute("innerHTML"))
            contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el['hasPart']['value']})
        except:
            error_type, error_obj, error_info = sys.exc_info()
            print ('ERROR FOR LINK:', link)
            print (error_type, 'Line:', error_info.tb_lineno)
            continue

    return contents

# df = pd.read_csv('data/washingtonpost_links.csv')
# links = df['URL'].values.tolist()
# contents = getContent(links)
# df = pd.DataFrame(contents)
# df.to_csv('data/washingtonpost_contents.csv', index=False)
