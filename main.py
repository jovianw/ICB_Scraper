import scrapers
import logging
import json
from selenium import webdriver

logging.basicConfig()
logging.root.setLevel('INFO')
 
def runAllJSON(keyPhrase, numLinks, dir="data"):
    for module in scrapers.Scrapers:
        jsonList = module.getJSON(keyPhrase=keyPhrase, numLinks=numLinks, webdriverOptions=options)
        with open(f"{dir}/{module.__name__}.json", "w") as outfile:
            json.dump(jsonList, outfile)

verbose = True
keyPhrase = "Walmart Groceries"
numLinks = 18
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

runAllJSON(keyPhrase, numLinks)