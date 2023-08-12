from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "USAToday"

    def getSearchLink(*args, **kwargs):
        return f"https://www.usatoday.com/search/?q={kwargs['keyPhrase']}&page={kwargs['page']}"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//div[contains(concat(' ', @class, ' '), ' gnt_pr ')]/a[not(contains(@href, 'reviewed.usatoday.com'))]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        el = browser.find_element(By.XPATH, "//script[@type='application/ld+json']")
        jsonDict = json.loads(el.get_attribute("innerHTML"))
        while type(jsonDict) is list:
            jsonDict = jsonDict[0]
        # Add articleBody
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//article//div[contains(concat(' ', @class, ' '), ' gnt_ar_b ')]//p[contains(concat(' ', @class, ' '), ' gnt_ar_b_p ')]"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict