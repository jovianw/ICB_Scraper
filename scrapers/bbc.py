from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "BBC"

    def getSearchLink(*args, **kwargs):
        return f"https://www.bbc.co.uk/search?q={kwargs['keyPhrase']}&page={['page']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//ul[contains(concat(' ', @class, ' '), ' ssrcss-1020bd1-Stack ')]/li//a[contains(@href,'bbc.co.uk/news')]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//main[@id='main-content']//article//p"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict
    
    def getJSON(self, keyPhrase, numLinks):
        links = self.getLinks(keyPhrase, numLinks)
        links = [re.sub(r"bbc\.co\.uk", 'bbc.com', link) for link in links]
        logging.root.info(links)
        return self.getJSONFromLinks(links)