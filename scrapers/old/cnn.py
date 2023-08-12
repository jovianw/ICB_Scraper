
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions as EX
import re
import logging
import json
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
        logging.root.info(f"CNN: Getting new page...")
        size = numLinks if numLinks < 50 else 50
        search_link = f"https://www.cnn.com/search?q={keyPhrase}&from={size * (page - 1)}&size={size}&page={page}&sort=relevance&types=article&section="
        # Get next page
        try:
            browser.get(search_link)
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.CLASS_NAME, "container__link"))
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
            # Get link
            try:
                browser.get(link)
            except ReadTimeoutError: # If connection error, try reseting browser
                logging.root.info("ReadTimeoutError, attempting to reset browser...")
                browser = webdriver.Chrome(options=webdriverOptions)
                browser.command_executor.set_timeout(patience) # Control process wait limit
                wait = WebDriverWait(browser, patience) # Page wait limit
                browser.get(link)
            if "money.cnn.com" in link:
                # Find metadata
                elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@name][@content]"))
                jsonDict = {}
                for elem in elems:
                    jsonDict[elem.get_attribute("name")] = elem.get_attribute("content")
                contents.append(jsonDict)
            else:
                # Find json data
                el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
                contents.append(json.loads(el.get_attribute("innerHTML")))
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Can't find content of page {link}, skipping...")
            break
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, skipping...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, patience=10, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, patience, webdriverOptions)
    logging.root.info(links)
    return getJSONFromLinks(links, patience, webdriverOptions)