from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "APNews"

    def getSearchLink(*args, **kwargs):
        return f"https://apnews.com/search?q={kwargs['keyPhrase']}&f2=00000188-f942-d221-a78c-f9570e360000&s=0&p={kwargs['page']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//div[contains(concat(' ', @class, ' '), ' SearchResultsModule-results ')]//div[contains(concat(' ', @class, ' '), ' PagePromo-title ')]/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' RichTextStoryBody ')]/p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict