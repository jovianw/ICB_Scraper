from abc import ABC, abstractmethod
import logging


class AbstractScraper(ABC):
    @abstractmethod
    def getJSON(self, keyPhrase, numLinks):
        pass


class WebScraper(AbstractScraper):
    @abstractmethod
    def getLinks(self, keyPhrase, numLinks):
        pass

    @abstractmethod
    def getJSONFromLinks(self, links):
        pass

    def getJSON(self, keyPhrase, numLinks):
        links = self.getLinks(keyPhrase, numLinks)
        logging.root.info(links)
        return self.getJSONFromLinks(links)