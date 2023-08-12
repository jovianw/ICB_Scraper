from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
from urllib3.exceptions import ReadTimeoutError

def getLinks(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    if numLinks < 1:
        return []
    links = []
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '+', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    wait = WebDriverWait(browser, patience) # Page wait limit
    page = 1
    # Do while not numLinks
    while len(links) < numLinks:
        logging.root.info(f"BBC: Getting new page...")
        try:
            browser.get(f'https://www.bbc.co.uk/search?q={keyPhrase}&page={page}')
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//ul[contains(concat(' ', @class, ' '), ' ssrcss-1020bd1-Stack ')]/li//a[contains(@href,'bbc.co.uk/news')]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"TimoutException: Probably due to lack of search results. Requested {numLinks} links, only found {len(links)}. Continuing...")
            break
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck getting search page, continuing...")
            break
        page += 1
    return links


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
            link = re.sub(r"bbc\.co\.uk", 'bbc.com', link)
            # Get link
            try:
                browser.get(link)
            except ReadTimeoutError: # If connection error, try reseting browser
                logging.root.info("ReadTimeoutError, attempting to reset browser...")
                browser = webdriver.Chrome(options=webdriverOptions)
                browser.command_executor.set_timeout(patience) # Control process wait limit
                wait = WebDriverWait(browser, patience) # Page wait limit
                browser.get(link)
            # Find metadata
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            jsonDict = json.loads(el.get_attribute("innerHTML"))
            # Add articleBody
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//main[@id='main-content']//article//p"))
            jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
            contents.append(jsonDict)
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, continuing...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, patience, webdriverOptions)
    logging.root.info(links)
    return getJSONFromLinks(links, patience, webdriverOptions)