from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    if numLinks < 1:
        return []
    links = []
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '%20', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    page = 0
    # Do while not numLinks
    while True:
        logging.root.info(f"Getting new page...")
        try:
            browser.get(f'https://www.latimes.com/search?q={keyPhrase}&f1=0000016a-ea2d-db5d-a57f-fb2dc8680000&s=0&p={page}')
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//ul[@class='search-results-module-results-menu']/li//div[contains(concat(' ', @class, ' '), ' promo-media ')]/a[@href]"))
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


# def getContent(links):
#     browser = webdriver.Chrome(options=webdriverOptions)
#     contents = []

#     for link in links:
#         try:
#             browser.get(link)
#             el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
#             parsed_el = json.loads(el.get_attribute("innerHTML"))
#             contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el.get('articleBody')})
#         except Exception as err:
#             warnings.warn(f"{type(err)}: {err}")
#             warnings.warn('ERROR FOR LINK:', link)
#             continue

#     return contents


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
            # Get link
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


def getJSON(keyPhrase, numLinks, webdriverOptions=None):
    links = getLinks(keyPhrase, numLinks, webdriverOptions)
    return getJSONFromLinks(links, webdriverOptions)


# def getJSON(keyPhrase, numLinks, webdriverOptions=None):
#     links = getLinks(keyPhrase, numLinks, webdriverOptions)
#     print(links)
#     print(len(links))