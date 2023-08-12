from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *
from selenium.webdriver.support import expected_conditions as EC

class Scraper(GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "ABC"
        self.searchLink = "https://abcnews.go.com/search?searchtext={keyPhrase}&type=Story&page={page}"

    def getLinks(self, keyPhrase, numLinks):
        if numLinks < 1:
            return []
        links = []
        # Reformat keyphrase
        keyPhrase = formatKeyPhrase(keyPhrase=keyPhrase)
        # Start selenium browser
        browser, wait = browserStart(patience=self.patience, webdriverOptions=self.webdriverOptions)
        # Get first page
        try:
            logging.root.info(f"{self.name}: Getting new search page...")
            browser, wait = browserGet(browser, wait, f"https://www.nbcnews.com/search/?q={keyPhrase}")
            # Get all links
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                            "//div[contains(concat(' ',normalize-space(@class),' '),' gsc-thumbnail-inside ')]//a[@class='gs-title' and @href]"))
            links.extend([elem.get_attribute("href") for elem in elems])
        except EX.TimeoutException: # If wait timed out
            logging.root.warning(
                    f"{self.name}: TimoutException, probably due to lack of search results. Requested {numLinks} links, only found {len(links)}. Continuing...")
            return []
        except EX.NoSuchWindowException as err: # If window has somehow been closed
            raise err
        except Exception as err: # Otherwise
            logging.root.warning(f'{self.name}: {type(err)} {err} {traceback.format_exc()}')
            logging.root.warning(f"Stuck getting search page, continuing...")
            return []
        page = 2
        # Do while not numLinks
        while len(links) < numLinks:
            logging.root.info(f"{self.name}: Getting new search page...")
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
                logging.root.warning(
                    f"{self.name}: TimoutException, probably due to lack of search results. Requested {numLinks} links, only found {len(links)}. Continuing...")
                break
            except EX.NoSuchWindowException as err: # If window has somehow been closed
                raise err
            except Exception as err: # Otherwise
                logging.root.warning(f'{self.name}: {type(err)} {err} {traceback.format_exc()}')
                logging.root.warning(f"Stuck getting search page, continuing...")
                break
            page += 1
        return links
    
    def getArticleData(self, browser, wait, link):
        # Find json data
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        return json.loads(el.get_attribute("innerHTML"))