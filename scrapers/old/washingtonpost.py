
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
import time
from urllib3.exceptions import ReadTimeoutError

def getLinks(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    if numLinks < 1:
        return []
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '+', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    wait = WebDriverWait(browser, patience) # Page wait limit
    # Get search page
    browser.get(f'https://www.washingtonpost.com/search/?query={keyPhrase}&time=all&sort=relevancy')
    elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                 "//article[contains(concat(' ',normalize-space(@class),' '),' single-result ')]//a[@href and contains(concat(' ',normalize-space(@class),' '),'font-md')]"))
    # Do while not numLinks
    while len(elems) < numLinks:
        logging.root.info(f"WashingtonPost: Getting new page...")
        try:
            # Click load more
            elem = wait.until(lambda d: d.find_element(By.XPATH, "//button[.='Load more results']"))
            elem.click()
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"TimoutException: Probably due to lack of search results. Requested {numLinks} links, only found {len(elems)}. Continuing...")
            break
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get new page, skipping...")
            break
        # Wait for more results
        time.sleep(1)
        elems = browser.find_elements(By.XPATH, 
                                      "//article[contains(concat(' ',normalize-space(@class),' '),' single-result ')]//a[@href and contains(concat(' ',normalize-space(@class),' '),'font-md')]")
    return [elem.get_attribute("href") for elem in elems]


def getJSONFromLinks(links, patience=10, webdriverOptions=None):
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    wait = WebDriverWait(browser, patience) # Page wait limit
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
                wait = WebDriverWait(browser, patience) # Page wait limit
                browser.get(link)
            # Find json data
            el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
            contents.append(json.loads(el.get_attribute("innerHTML")))
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err:
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, skipping...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, patience, webdriverOptions)
    logging.root.info(links)
    return getJSONFromLinks(links, patience, webdriverOptions)