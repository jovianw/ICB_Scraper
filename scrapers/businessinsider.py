from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "BusinessInsider"

    def getSearchLink(*args, **kwargs):
        return f"https://www.businessinsider.com/s?q={kwargs['keyPhrase']}&p={kwargs['page']-1}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//section[contains(concat(' ', @class, ' '), ' js-feed-item ')]//a[contains(concat(' ', @class, ' '), ' tout-title-link ')][@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find json data
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        return json.loads(el.get_attribute("innerHTML"))