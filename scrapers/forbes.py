from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksScrollMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "Forbes"

    def getSearchLink(*args, **kwargs):
        return f"https://www.forbes.com/search/?q={kwargs['keyPhrase']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, "//article//h3/a[contains(@href,'/sites/')]")
    
    def getSearchButton(self, d):
        return d.find_element(By.CLASS_NAME, "search-more")

    def getArticleData(self, browser, wait, link):
        # Find json data
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        elems = browser.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' article-body ')]/p")
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict