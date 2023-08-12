from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "NYPost"

    def getSearchLink(*args, **kwargs):
        return f"https://nypost.com/search/{kwargs['keyPhrase']}/page/{kwargs['page']}/?orderby=relevance"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//div[contains(concat(' ', @class, ' '), ' search-results__story ')]//h3[contains(concat(' ', @class, ' '), ' story__headline ')]/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find json data
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add description
        description_el = wait.until(lambda d: d.find_element(By.XPATH, "//meta[@name='sailthru.description']"))
        jsonDict['description'] = description_el.get_attribute("content")
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' entry-content ')]/p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict