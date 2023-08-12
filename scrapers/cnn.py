from scrapers.common.scraper import WebScraper
from scrapers.common.helpers import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common import exceptions as EX
import logging
import json

class Scraper(GetLinksPagedMixin, GetJSONFromLinksMixin, WebScraper):
    def __init__(self, patience=10, webdriverOptions=None):
        self.patience = patience
        self.webdriverOptions = webdriverOptions
        self.name = "CNN"

    def getSearchLink(*args, **kwargs):
        size = kwargs['numLinks'] if kwargs['numLinks'] < 50 else 50
        return f"https://www.cnn.com/search?q={kwargs['keyPhrase']}&from={size * (kwargs['page'] - 1)}&size={size}&page={kwargs['page']}&sort=relevance&types=article&section="

    def getLinksFromSearch(self, d):
        return d.find_elements(By.CLASS_NAME, "container__link")

    def getArticleData(self, browser, wait, link):
        if "money.cnn.com" in link:
            # Find metadata
            elems = wait.until(lambda d: d.find_elements(By.XPATH, "//meta[@name][@content]"))
            jsonDict = {}
            for elem in elems:
                jsonDict[elem.get_attribute("name")] = elem.get_attribute("content")
            return jsonDict
        else:
            # Find json data
            el = wait.until(lambda d: d.find_element(By.XPATH, "//script[@type='application/ld+json']"))
            return json.loads(el.get_attribute("innerHTML"))
