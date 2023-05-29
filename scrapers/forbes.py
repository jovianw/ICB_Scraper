
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
    return '%s:%s: %s:\n%s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line
warnings.simplefilter('always', UserWarning)

def getLinks(keyword, pagesToGet):
    if pagesToGet < 1:
        warnings.warn("Can't get less than 1 pages")
        return []
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)

    url = 'https://www.forbes.com/search/?q=' + keyword
    browser.get(url)

    # Wait until results are loaded
    # elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article//h2[@class='title']/a[@href]"))

    # Press load more
    for page in range(2, pagesToGet + 1):
        # Get next page
        try:
            browser.find_element(By.CLASS_NAME, "search-more").click()
        except:
            warnings.warn("Stuck attempting to get page %d, skipping..." % page)
            break
        time.sleep(1)

    elems = browser.find_elements(By.XPATH, "//article//h3/a[@href]")
    return [elem.get_attribute("href") for elem in elems]


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/forbes_links.csv', index=False)


def getContent(links):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-certificate-error')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')
    browser = webdriver.Chrome(options=options)
    contents = []

    for link in links:
        # Just skip over video results for now
        if "www.forbes.com/video" in link:
            continue
        try:
            browser.delete_all_cookies()
            browser.get(link)
            # Get headline and description
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            parsed_el = json.loads(el.get_attribute("innerHTML"))
            headline = parsed_el['headline']
            description = parsed_el['description']
            # Get article body
            elems = browser.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' article-body ')]/p")
            articleBody = ' '.join([elem.text for elem in elems])
            contents.append({'Headline': headline, 'Description': description, 'Content': articleBody})
        except:
            error_type, error_obj, error_info = sys.exc_info()
            warnings.warn('ERROR FOR LINK: %s' % str(link))
            warnings.warn('%s\nLine: %s' % (str(error_type), str(error_info.tb_lineno)))
            continue

    return contents

df = pd.read_csv('data/forbes_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/forbes_contents.csv', index=False)
