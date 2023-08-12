from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re
from selenium.common import exceptions as EX
import logging
from urllib3.exceptions import ReadTimeoutError
from abc import ABC, abstractmethod
import time
import traceback

######## FUNCTIONS ########

def formatKeyPhrase(keyPhrase):
    """
    Helper to format keyphrase in a url-friendly way
    """
    result = re.sub(r"[^\w\s]", '', keyPhrase)
    result = re.sub(r"\s+", '+', result)
    return result


def browserStart(patience=10, webdriverOptions=None):
    """
    Default starting a selenium browser
    """
    browser = webdriver.Chrome(options=webdriverOptions)
    browser.command_executor.set_timeout(patience) # Control process wait limit
    wait = WebDriverWait(browser, patience) # Page wait limit
    return browser, wait


def browserGet(browser, wait, link, maxAttempts=3, patience=10, webdriverOptions=None):
    for i in range(maxAttempts):
        try:
            browser.get(link)
        except ReadTimeoutError as err: # If connection error, try reseting browser
            if i == maxAttempts-1:
                raise err
            logging.root.info("ReadTimeoutError, attempting to reset browser...")
            browser.close()
            time.sleep(1)
            browser = webdriver.Chrome(options=webdriverOptions)
            browser.command_executor.set_timeout(patience) # Control process wait limit
            wait = WebDriverWait(browser, patience) # Page wait limit
            continue
        return browser, wait
    

######## DEFAULT MIXINS #########

class GetLinksPagedMixin(ABC):
    @abstractmethod
    def getSearchLink(*args, **kwargs):
        pass

    @abstractmethod
    def getLinksFromSearch(self, d):
        pass

    def getLinks(self, keyPhrase, numLinks):
        """
        Default function to get links from a paginated search page
        keyPhrase: raw key phrase
        numLinks: number of requested links

        Returns list of article links
        """
        if numLinks < 1:
            return []
        links = []
        # Reformat keyphrase
        keyPhrase = formatKeyPhrase(keyPhrase=keyPhrase)
        # Start selenium browser
        browser, wait = browserStart(patience=self.patience, webdriverOptions=self.webdriverOptions)
        page = 1
        retries = 0
        # Do while not numLinks
        while len(links) < numLinks:
            if retries > self.patience: # Call it a day if we looped too many times
                logging.root.warning(f"{self.name}: Max retries, continuing...")
                break
            logging.root.info(f"{self.name}: Getting new search page...")
            try:
                browser, wait = browserGet(browser, wait, self.getSearchLink(**locals()))
                # Get all links
                elems = wait.until(self.getLinksFromSearch)
                links.extend([elem.get_attribute("href") for elem in elems])
            except EX.StaleElementReferenceException: # If something went stale
                logging.root.warning(f"{self.name}: StaleElementReferenceException, retrying...")
                retries += 1
                continue
            except EX.TimeoutException: # If wait timed out
                logging.root.warning(
                    f"{self.name}: TimoutException, probably due to lack of search results matching criteria. Requested {numLinks} links, only found {len(links)}. Continuing...")
                break
            except EX.NoSuchWindowException as err: # If window has somehow been closed
                # browser.quit()
                raise err
            except Exception as err: # Otherwise
                logging.root.warning(f'{self.name}: {type(err)} {err} {traceback.format_exc()}')
                logging.root.warning(f"{self.name}: Stuck getting search page, continuing...")
                break
            page += 1
        # browser.quit()
        return links
    

class GetLinksScrollMixin(ABC):
    @abstractmethod
    def getSearchLink(*args, **kwargs):
        pass

    @abstractmethod
    def getLinksFromSearch(self, d):
        pass

    @abstractmethod
    def getSearchButton(self, d):
        pass

    def getLinks(self, keyPhrase, numLinks):
        """
        Default function to get links from a infinite scrolling search page
        keyPhrase: raw key phrase
        numLinks: number of requested links

        Returns list of article links
        """
        if numLinks < 1:
            return []
        # Reformat keyphrase
        keyPhrase = formatKeyPhrase(keyPhrase=keyPhrase)
        # Start selenium browser
        browser, wait = browserStart(patience=self.patience, webdriverOptions=self.webdriverOptions)
        # Go to page
        browser, wait = browserGet(browser, wait, self.getSearchLink(**locals()))
        elems = wait.until(self.getLinksFromSearch)
        retries = 0
        # Do while not numLinks
        while len(elems) < numLinks:
            if retries > self.patience: # Call it a day if we looped too many times
                logging.root.warning(f"{self.name}: Max retries, continuing...")
                break
            logging.root.info(f"{self.name}: Getting new page...")
            try:
                # Click load more
                elem = wait.until(self.getSearchButton)
                elem.click()
            except EX.StaleElementReferenceException: # If something went stale
                logging.root.warning(f"{self.name}: StaleElementReferenceException, retrying...")
                retries += 1
                continue
            except EX.TimeoutException: # If wait timed out
                logging.root.warning(
                    f"{self.name}: TimoutException, probably due to lack of search results matching criteria. Requested {numLinks} links, only found {len(elems)}. Continuing...")
                break
            except EX.NoSuchWindowException as err: # If window has somehow been closed
                # browser.quit()
                raise err
            except Exception as err: # Otherwise
                logging.root.warning(f'{self.name}: {type(err)} {err} {traceback.format_exc()}')
                logging.root.warning(f"{self.name}: Stuck attempting to get new page, skipping...")
                break
            # Wait for new results
            time.sleep(1)
            elems = self.getLinksFromSearch(browser)
        # browser.quit()
        return [elem.get_attribute("href") for elem in elems]


class GetJSONFromLinksMixin:
    @abstractmethod
    def getArticleData(self, browser, wait, link):
        pass

    def getJSONFromLinks(self, links):
        """
        Default function to get JSON data from linked articles
        links: list of article links

        Returns list of dictionaries
        """
        # Start selenium browser
        browser, wait = browserStart(patience=self.patience, webdriverOptions=self.webdriverOptions)
        contents = []
        count = 0
        for link in links:
            count += 1
            logging.root.info(f"({count}/{len(links)}) Visiting {link}...")
            try:
                # Get link
                browser, wait = browserGet(browser, wait, link)
                # Find article data
                jsonDict = self.getArticleData(browser, wait, link)
                contents.append(jsonDict)
            except EX.NoSuchWindowException as err: # If window has somehow been closed
                # browser.quit()
                raise err
            except Exception as err: # Otherwise
                logging.root.warning(f'{self.name}: {type(err)} {err} {traceback.format_exc()}')
                logging.root.warning(f"{self.name}: Error for link {link}, continuing...")
                continue
        # browser.quit()
        return contents