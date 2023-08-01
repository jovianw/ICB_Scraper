from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
from selenium.webdriver.support import expected_conditions as EC
import logging

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    if numLinks < 1:
        return []
    links = []
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '+', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    page = 1
    # Do while not numLinks
    while True:
        logging.root.info(f"Getting new page...")
        try:
            browser.get(f'https://www.bbc.co.uk/search?q={keyPhrase}&page={page}')
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//ul[contains(concat(' ', @class, ' '), ' ssrcss-1020bd1-Stack ')]/li//a[@href]"))
            links.extend([elem.get_attribute("href") for elem in elems if "bbc.co.uk/news" in elem.get_attribute("href")]) # manually filter only for news
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Requested {numLinks} links, only found {len(links)}, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        # except EX.StaleElementReferenceException:
        #     continue
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get new page, skipping...")
            break
        # Break if numLinks
        if len(links) >= numLinks:
            break
        page += 1
    return links


def getJSONFromLinks(links, webdriverOptions=None):
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    contents = []
    count = 0
    for link in links:
        count += 1
        logging.root.info(f"({count}/{len(links)}) Visiting {link}...")
        try:
            link = re.sub(r"bbc\.co\.uk", 'bbc.com', link)
            # Get link
            browser.get(link)
            # Find metadata
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            jsonDict = json.loads(el.get_attribute("innerHTML"))
            # Add articleBody
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//main[@id='main-content']//article//p"))
            jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
            contents.append(jsonDict)
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err:
            logging.root.warning(f"{type(err)}: {err}")
            logging.root.warning(f"Error for link {link}, skipping...")
            continue
    return contents


def getJSON(keyPhrase, numLinks, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, webdriverOptions)
    print(links)
    return getJSONFromLinks(links, webdriverOptions)