from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksScrollMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "Fox"

    def getSearchLink(*args, **kwargs):
        return f"https://www.foxnews.com/search-results/search?q={kwargs['keyPhrase']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, "//article//h2[@class='title']/a[not(contains(@href, 'foxnews.com/category'))]")
    
    def getSearchButton(self, d):
        return d.find_element(By.XPATH, "//div[contains(concat(' ',normalize-space(@class),' '),' load-more ')]/a")
    
    def getArticleData(self, browser, wait, link):
         # Find json data
        el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
        return json.loads(el.get_attribute("innerHTML"))