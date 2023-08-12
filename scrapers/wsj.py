from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "WSJ"

    def getSearchLink(*args, **kwargs):
        return f"https://www.wsj.com/search?query={kwargs['keyPhrase']}&isToggleOn=true&operator=OR&sort=relevance&source=wsjie%2Cblog%2Cwsjpro&page={kwargs['page']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//article[not(contains(@class, 'WSJTheme--sponsored-story--35YuMRMD'))]//h3/a[@href]")
    
    def getArticleData(self, browser, wait, link):
         # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDictList = json.loads(el.get_attribute("innerHTML"))
        jsonDict = [x for x in jsonDictList if x['@type'] == 'NewsArticle'][0]
        return jsonDict