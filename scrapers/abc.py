from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "ABC"

    def getSearchLink(*args, **kwargs):
        return f"https://abcnews.go.com/search?searchtext={kwargs['keyPhrase']}&type=Story&page={kwargs['page']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//div[contains(concat(' ', @class, ' '), ' ContentRoll__Headline ')]/h2/a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        if "goodmorningamerica.com" in link:
            elems = wait.until(lambda d: d.find_elements(By.XPATH, 
                                                            "//section[contains(concat(' ', @class, ' '), ' article-body ')]//div[contains(concat(' ', @class, ' '), ' fitt-tracker ')]//p"))
        else:
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article/p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict