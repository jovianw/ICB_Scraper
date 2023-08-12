from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "Politico"

    def getSearchLink(*args, **kwargs):
        return f"https://www.politico.com/search/{kwargs['page']}?q={kwargs['keyPhrase']}&adv=true&c=a9d449a5-b61d-32fc-b70c-e15227dcdca7"

    def getLinksFromSearch(self, d):
        return d.find_elements(By.XPATH, 
                               "//article[contains(concat(' ', @class, ' '), ' story-frag ')]//header//a[@href]")
    
    def getArticleData(self, browser, wait, link):
        # Find metadata
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@name][@content]"))
        jsonDict = {}
        for elem in elems:
            jsonDict[elem.get_attribute("name")] = elem.get_attribute("content")
        elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@property][@content]"))
        for elem in elems:
            jsonDict[elem.get_attribute("property")] = elem.get_attribute("content")
        # Add articleBody
        if "politicopro.com/" in link:
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' media-article__text ')]/p"))
        else:
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//p[contains(concat(' ', @class, ' '), ' story-text__paragraph ')]"))
        jsonDict['articleBody'] = ' '.join([elem.text for elem in elems])
        return jsonDict