from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
from selenium.webdriver.support import expected_conditions as EC

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
    # Get first page
    try:
        browser.get(f"https://www.nbcnews.com/search/?q={keyPhrase}")
        # Get all links
        elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                        "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]"))
        links.extend([elem.get_attribute("href") for elem in elems])
    except EX.TimeoutException: # If wait timed out
        logging.root.warning(f"Requested {numLinks} links, only found {len(links)}, skipping...")
        return []
    except EX.NoSuchWindowException as err:
        raise err
    except Exception as err: # Otherwise
        logging.root.warning(f'{type(err)} Line: {err}')
        logging.root.warning(f"Stuck attempting to get new page, skipping...")
        return []
    page = 2
    # Do while not numLinks
    while len(links) < numLinks:
        logging.root.info(f"Getting new page...")
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
            logging.root.warning(f"Requested {numLinks} links, only found {len(links)}, skipping...")
            break
        except EX.NoSuchWindowException as err:
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{type(err)} Line: {err}')
            logging.root.warning(f"Stuck attempting to get new page, skipping...")
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


# def getJSON(keyPhrase, numLinks, webdriverOptions=None):
#     links = getLinks(keyPhrase, numLinks, webdriverOptions)
#     print(links)
#     print(len(links))
