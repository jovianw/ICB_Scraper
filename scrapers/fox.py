from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
import time

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    if numLinks < 1:
        return []
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '%20', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    browser.get(f'https://www.foxnews.com/search-results/search?q={keyPhrase}')
    elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article//h2[@class='title']/a[@href]"))
    # Do while not numLinks
    while len(elems) < numLinks:
        logging.root.info(f"Getting new page...")
        try:
            # Click load more
            elem = wait.until(lambda d: d.find_element(By.XPATH, "//div[contains(concat(' ',normalize-space(@class),' '),' load-more ')]/a"))
            elem.click()
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Requested {numLinks} links, only found {len(elems)}, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get new page, skipping...")
            break
        time.sleep(1)
        elems = browser.find_elements(By.XPATH, "//article//h2[@class='title']/a[@href]")
    return [elem.get_attribute("href") for elem in elems]


# def getContent(links):
#     browser = webdriver.Chrome(options=webdriverOptions)
#     contents = []

#     for link in links:
#         # Just skip over video results for now
#         if "www.foxnews.com/video" in link:
#             continue
#         try:
#             browser.get(link)
#             el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
#             parsed_el = json.loads(el.get_attribute("innerHTML"))
#             contents.append({'Headline': parsed_el['headline'], 'Description': parsed_el['description'], 'Content': parsed_el['articleBody']})
#         except:
#             error_type, error_obj, error_info = sys.exc_info()
#             print ('ERROR FOR LINK:', link)
#             print (error_type, 'Line:', error_info.tb_lineno)
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


