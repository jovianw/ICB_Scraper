import json
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as EX
import logging
from urllib3.exceptions import ReadTimeoutError

def getLinks(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    if numLinks < 1:
        return []
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    wait = WebDriverWait(browser, patience) # Page wait limit
    browser.set_window_size(1920, 1080) # Necessary for this one
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
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))
    # Do while not numLinks
    while len(elems) < numLinks:
        logging.root.info(f"CBS: Getting new page...")
        # Get next page
        try:
            elem = wait.until(lambda d: d.find_element(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//a[@data-name='endindex'][last()]"))
            elem.click()
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"TimoutException: Probably due to lack of search results. Requested {numLinks} links, only found {len(elems)}. Continuing...")
            break
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck getting search page, continuing....")
            break
        # Wait for new results
        time.sleep(1)
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))
    return [elem.get_attribute("href") for elem in elems]


def getJSONFromLinks(links, patience=10, webdriverOptions=None):
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    contents = []
    count = 0
    for link in links:
        count += 1
        logging.root.info(f"({count}/{len(links)}) Visiting {link}...")
        try:
            # Get link
            try:
                browser.get(link)
            except ReadTimeoutError: # If connection error, try reseting browser
                logging.root.info("ReadTimeoutError, attempting to reset browser...")
                browser = webdriver.Chrome(options=webdriverOptions)
                browser.command_executor.set_timeout(patience) # Control process wait limit
                browser.get(link)
            # Find json data
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            contents.append(json.loads(el.get_attribute("innerHTML")))
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err:
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, continuing...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, patience, webdriverOptions)
    logging.root.info(links)
    return getJSONFromLinks(links, patience, webdriverOptions)