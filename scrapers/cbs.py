from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions as EX
import logging

class Scraper(GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "CBS"

    def getLinks(self, keyPhrase, numLinks):
        if numLinks < 1:
            return []
        # Start selenium browser
        browser, wait = browserStart(patience=self.patience, webdriverOptions=self.webdriverOptions)
        browser.set_window_size(1920, 1080) # Necessary for this one
        # Load twice to get to search
        browser.get("https://www.cbsnews.com/#search-form:")
        browser.get("https://www.cbsnews.com/#search-form:")
        # Search and enter
        searchField = wait.until(lambda d: d.find_element(By.CLASS_NAME, "search-field"))
        searchField.send_keys(keyPhrase)
        searchField.send_keys(Keys.ENTER)
        # Filter by articles
        articleFilter = wait.until(lambda d: d.find_element(By.XPATH, '//input[@id="search-facet--contenttype-news"]/following-sibling::label'))
        articleFilter.click()
        # Wait until results are loaded
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))
        # Do while not numLinks
        while len(elems) < numLinks:
            logging.root.info(f"CBS: Getting new page...")
            # Get next page
            try:
                elem = wait.until(lambda d: d.find_element(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//a[@data-name='endindex'][last()]"))
                elem.click()
            except EX.TimeoutException: # If wait timed out
                logging.root.warning(f"TimoutException: Probably due to lack of search results. Requested {numLinks} links, only found {len(elems)}. Continuing...")
                break
            except EX.NoSuchWindowException as err: # If window has somehow been closed
                raise err
            except Exception as err: # Otherwise
                logging.root.warning(f'{type(err)} Line: {err}')
                logging.root.warning(f"Stuck getting search page, continuing....")
                break
            # Wait for new results
            time.sleep(1)
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//section[contains(concat(' ', @class, ' '), ' search-results ')]//article/a"))
        browser.quit()
        return [elem.get_attribute("href") for elem in elems]
    
    def getArticleData(self, browser, wait, link):
        # Find json data
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        return json.loads(el.get_attribute("innerHTML"))