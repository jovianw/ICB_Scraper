from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
from selenium.webdriver.support import expected_conditions as EC
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
    # Get first page
    try:
        browser.get(f"https://www.nbcnews.com/search/?q={keyPhrase}")
        # Get all links
        elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                        "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]"))
        links.extend([elem.get_attribute("href") for elem in elems])
    except EX.TimeoutException: # If wait timed out
        logging.root.warning(f"TimoutException: Probably due to lack of search results. Requested {numLinks} links, only found {len(links)}. Continuing...")
        return []
    except EX.NoSuchWindowException as err: # If window has somehow been closed
        raise err
    except Exception as err: # Otherwise
        logging.root.warning(f'{type(err)} Line: {err}')
        logging.root.warning(f"Stuck getting search page, continuing...")
        return []
    page = 2
    # Do while not numLinks
    while len(links) < numLinks:
        logging.root.info(f"NBC: Getting new page...")
        try:
            # Get next page
            browser.find_element(By.XPATH, "//div[@class='gsc-cursor']/div[.='%d']" % page).click()
            # Wait until new results have loaded
            wait.until(EC.staleness_of(elems[0]))
            wait.until_not(lambda d: d.find_element(By.CLASS_NAME, "gsc-loading-fade"))
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except (EX.TimeoutException, EX.StaleElementReferenceException): # If wait timed out
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