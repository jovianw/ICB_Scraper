from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions as EX
import logging
import json
import re


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
    page = 0
    # Do while not numLinks
    while True:
        logging.root.info(f"Getting new page...")
        try:
            browser.get(f'https://www.businessinsider.com/s?q={keyPhrase}&p={page}')
            # Get all links
            elems = wait.until(
                lambda d: d.find_elements(By.XPATH, 
                                          "//section[contains(concat(' ', @class, ' '), ' js-feed-item ')]//a[contains(concat(' ', @class, ' '), ' tout-title-link ')][@href]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Requested {numLinks} links, only found {len(links)}, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get new page, skipping...")
            break
        # Break if numLinks
        if len(links) >= numLinks:
            break
        page += 1
    return links


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
            contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el.get('articleBody')})
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