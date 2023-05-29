import urllib.request,sys,time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import warnings
import json

keyword = "Walmart"
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

    url = 'https://www.businessinsider.com/s?q=' + keyword
    browser.get(url)

    # Wait until results are loaded
    wait.until(lambda d: d.find_elements(By.CLASS_NAME, "js-feed-item"))

    # Press button for more pages
    if pagesToGet > 1:
        print("Getting page %d" % 2)
        try:
            browser.find_element(By.CLASS_NAME, "river-more-link").click()
        except:
            warnings.warn("Stuck attempting to get page 2, skipping...")
        else:
            # Press load more
            for page in range(3, pagesToGet+1):
                print("Getting page %d" % page)
                # Get next page
                try:
                    loader = browser.find_element(By.CLASS_NAME, "js-loader")
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    wait.until(EC.invisibility_of_element(loader))
                except Exception as err:
                    warnings.warn(f"{type(err)}: {err}")
                    warnings.warn(f"Stuck attempting to get page {page}, skipping...")
                    break

    elems = browser.find_elements(By.XPATH, 
                                  "//section[contains(concat(' ', @class, ' '), ' js-feed-item ')]//a[contains(concat(' ', @class, ' '), ' tout-title-link ')][@href]")
    return [elem.get_attribute("href") for elem in elems]


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/businessinsider_links.csv', index=False)


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

df = pd.read_csv('data/businessinsider_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/businessinsider_contents.csv', index=False)