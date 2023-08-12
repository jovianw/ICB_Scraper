from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksScrollMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "WashingtonPost"

    def getSearchLink(*args, **kwargs):
        return f"https://www.washingtonpost.com/search/?query={kwargs['keyPhrase']}&time=all&sort=relevancy"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//article[contains(concat(' ',normalize-space(@class),' '),' single-result ')]//a[@href and contains(concat(' ',normalize-space(@class),' '),'font-md')]")
    
    def getSearchButton(self, d):
        return d.find_element(By.XPATH, "//button[.='Load more results']")

    def getArticleData(self, browser, wait, link):
        # Find json data
        el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
        return json.loads(el.get_attribute("innerHTML"))