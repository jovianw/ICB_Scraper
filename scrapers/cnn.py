
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions as EX
import re
import logging
import json

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    if numLinks < 1:
        return []
    links = []
    # Calculate pages
    pagesToGet = -(numLinks // -50)
    # Reformat keyphrase
    keyPhrase = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhrase = re.sub(r"\s+", '+', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    for page in range(1, pagesToGet + 1):
        logging.root.info(f"Getting page {page}...")
        size = numLinks if numLinks < 50 else 50
        url = f"https://www.cnn.com/search?q={keyPhrase}&from={50 * (page - 1)}&size={size}&page={page}&sort=relevance&types=article&section="
        # Get next page
        try:
            browser.get(url)
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.CLASS_NAME, "container__link"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(f"Requested {numLinks} links ({pagesToGet} pages), only found {page} pages, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get page {page}, skipping...")
            break
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
            # Get link
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