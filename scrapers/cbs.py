import json
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as EX
import logging

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    if numLinks < 1:
        return []
    # Calculate pages
    pagesToGet = -(numLinks // -15)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.set_window_size(1920, 1080)
    wait = WebDriverWait(browser, 10)
    # Load twice to get to search
    browser.get("https://www.cbsnews.com/#search-form:")
    browser.get("https://www.cbsnews.com/#search-form:")
    # Search and enter
    searchField = wait.until(lambda d: d.find_element(By.CLASS_NAME, "search-field"))
    searchField.send_keys(keyPhrase)
    searchField.send_keys(Keys.ENTER)
    # Filter by articles
    articleFilter = wait.until(lambda d: d.find_element(By.XPATH, '//input[@id="search-facet--contenttype-news"]/following-sibling::label'))
    articleFilter.click()
    # Wait until results are loaded
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article"))
    # Press load more
    for page in range(2, pagesToGet + 1):
        logging.root.info(f"Getting page {page}...")
        # Get next page
        try:
            elem = wait.until(lambda d: d.find_element(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//a[@data-name='endindex'][last()]"))
            elem.click()
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Requested {numLinks} links ({pagesToGet} pages), only found {page} pages, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get page {page}, skipping...")
            break
        time.sleep(1)

    # Get all results
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))
    return [elem.get_attribute("href") for elem in elems]


def getContentFromLinks(links, webdriverOptions=None):
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    contents = []
    count = 0
    for link in links:
        count += 1
        logging.root.info(f"({count}/{len(links)}) Visiting {link}...")
        try:
            # Get link
            browser.get(link)
            # Find json data
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            parsed_el = json.loads(el.get_attribute("innerHTML"))
            contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el['articleBody']})
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err:
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, skipping...")
            continue
    return contents


def getJSONFromLinks(links, webdriverOptions=None):
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    contents = []
    count = 0
    for link in links:
        count += 1
        logging.root.info(f"({count}/{len(links)}) Visiting {link}...")
        try:
            # Get link
            browser.get(link)
            # Find json data
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            contents.append(json.loads(el.get_attribute("innerHTML")))
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err:
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, skipping...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, webdriverOptions)
    return getJSONFromLinks(links, webdriverOptions)