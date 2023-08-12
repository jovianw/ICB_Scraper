from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "LATimes"

    def getSearchLink(*args, **kwargs):
        return f"https://www.latimes.com/search?q={kwargs['keyPhrase']}&f1=0000016a-ea2d-db5d-a57f-fb2dc8680000&s=0&p={kwargs['page']-1}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, "//ul[@class='search-results-module-results-menu']/li//div[contains(concat(' ', @class, ' '), ' promo-media ')]/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find json data
        el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
        return json.loads(el.get_attribute("innerHTML"))