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
    page = 1
    # Do while not numLinks
    while True:
        logging.root.info(f"Getting new page...")
        try:
            browser.get(f'https://nypost.com/search/{keyPhrase}/page/{page}/?orderby=relevance')
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                         "//div[contains(concat(' ', @class, ' '), ' search-results__story ')]//h3[contains(concat(' ', @class, ' '), ' story__headline ')]/a[@href]"))
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
#     wait = WebDriverWait(browser, 10)
#     contents = []

#     for link in links:
#         try:
#             browser.get(link)
#             # Get headline and description
#             headline_el = wait.until(lambda d: d.find_element(By.XPATH, "//meta[@name='sailthru.title']"))
#             headline = headline_el.get_attribute("content")
#             description_el = browser.find_element(By.XPATH, "//meta[@name='sailthru.description']")
#             description = description_el.get_attribute("content")
#             # Get article body
#             elems = browser.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' entry-content ')]/p")
#             articleBody = ' '.join([elem.text for elem in elems])
#             contents.append({'Headline': headline, 'Description': description, 'Content': articleBody})
#         except:
#             error_type, _, error_info = sys.exc_info()
#             warnings.warn('ERROR FOR LINK: %s' % str(link))
#             warnings.warn('%s\nLine: %s' % (str(error_type), str(error_info.tb_lineno)))
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
            el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
            jsonDict = json.loads(el.get_attribute("innerHTML"))
            # Add description
            description_el = wait.until(lambda d: d.find_element(By.XPATH, "//meta[@name='sailthru.description']"))
            jsonDict['description'] = description_el.get_attribute("content")
            # Add articleBody
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' entry-content ')]/p"))
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
    return getJSONFromLinks(links, webdriverOptions)