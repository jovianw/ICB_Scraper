
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
pagesToGet = 10

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1 or pagesToGet > 10:
        raise Exception("Can only get 1-10 pages")
    links = []
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)

    url = 'https://www.nbcnews.com/search/?q='+keyword
    browser.get(url)

    # Wait until results are loaded
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]"))
    links.extend([elem.get_attribute("href") for elem in elems])

    for page in range(2, pagesToGet + 1):
        # Get next page
        browser.find_element(By.XPATH, "//div[@class='gsc-cursor']/div[.='%d']" % page).click()

        # Wait until new results have loaded
        wait.until(EC.staleness_of(elems[0]))
        wait.until_not(lambda d: d.find_element(By.CLASS_NAME, "gsc-loading-fade"))
        elems = browser.find_elements(By.XPATH, "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]")
        links.extend([elem.get_attribute("href") for elem in elems])
    
    return links


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/nbc_links.csv', index=False)


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
            print ('ERROR FOR LINK:', link)
            print (error_type, 'Line:', error_info.tb_lineno)
            continue

    return contents


# df = pd.read_csv('data/nbc_links.csv')
# links = df['URL'].values.tolist()
# contents = getContent(links)
# df = pd.DataFrame(contents)
# df.to_csv('data/nbc_contents.csv', index=False)

df = pd.read_csv('data/nbc_contents.csv')
