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
    keyPhrase = re.sub(r"\s+", '+', keyPhrase)
    # Start selenium browser
    browser = webdriver.Chrome(options=webdriverOptions)
    wait = WebDriverWait(browser, 10)
    page = 1
    # Do while not numLinks
    while True:
        logging.root.info(f"Getting new page...")
        try:
            browser.get(f'https://www.politico.com/search/{page}?q={keyPhrase}&adv=true&c=a9d449a5-b61d-32fc-b70c-e15227dcdca7')
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//article[contains(concat(' ', @class, ' '), ' story-frag ')]//header//a[@href]"))
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
            # Find metadata
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@name][@content]"))
            jsonDict = {}
            for elem in elems:
                jsonDict[elem.get_attribute("name")] = elem.get_attribute("content")
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@property][@content]"))
            for elem in elems:
                jsonDict[elem.get_attribute("property")] = elem.get_attribute("content")
            # Add articleBody
            if "politicopro.com/" in link:
                elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' media-article__text ')]/p"))
            else:
                elems = wait.until(lambda d: d.find_elements(By.XPATH, "//p[contains(concat(' ', @class, ' '), ' story-text__paragraph ')]"))
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