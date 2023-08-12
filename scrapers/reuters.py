from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "Reuters"

    def getSearchLink(*args, **kwargs):
        return f"https://www.reuters.com/site-search/?query={kwargs['keyPhrase']}&offset={(kwargs['page'] - 1) * 20}&sort=relevance"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//li[contains(concat(' ', @class, ' '), ' search-results__item__2oqiX ')]//h3/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' article-body__content__17Yit ')]//p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict