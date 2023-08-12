from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "Sun"

    def getSearchLink(*args, **kwargs):
        return f"https://www.the-sun.com/page/{kwargs['page']}/?s={kwargs['keyPhrase']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//div[contains(concat(' ', @class, ' '), ' teaser-item ')]/div[contains(concat(' ', @class, ' '), ' teaser__copy-container ')]/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' article__content ')]//p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict