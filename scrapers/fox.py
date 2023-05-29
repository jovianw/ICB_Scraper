
import urllib.request,sys,time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import json
import warnings

keyword = "Walmart"
pagesToGet= 10
def warning_on_one_line(message, category, filename, lineno, line=None):
    return '%s:%s: %s:\n%s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line
warnings.simplefilter('always', UserWarning)

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1:
        warnings.warn("Can't get less than 1 pages")
        return []
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)

    url = 'https://www.foxnews.com/search-results/search?q=' + keyword
    browser.get(url)

    # Wait until results are loaded
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article//h2[@class='title']/a[@href]"))

    # Press load more
    for page in range(2, pagesToGet + 1):
        # Get next page
        try:
            browser.find_element(By.XPATH, "//div[contains(concat(' ',normalize-space(@class),' '),' load-more ')]/a").click()
        except:
            warnings.warn("Stuck attempting to get page %d, skipping..." % page)
            break
        time.sleep(1)

    elems = browser.find_elements(By.XPATH, "//article//h2[@class='title']/a[@href]")
    return [elem.get_attribute("href") for elem in elems]


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/fox_links.csv', index=False)


def getContent(links):
    browser = webdriver.Chrome()
    contents = []

    for link in links:
        # Just skip over video results for now
        if "www.foxnews.com/video" in link:
            continue
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

df = pd.read_csv('data/fox_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/fox_contents.csv', index=False)
