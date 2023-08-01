import os
import requests
import logging
import time

API_KEY = os.getenv('NYTimes_Key')
keyword = "https://www.nytimes.com/2023/05/18/business/walmart-earnings-1q-2023.html"
pagesToGet= 5

def getLinks(keyPhrase, numLinks, webdriverOptions=None):
    pagesToGet = -(numLinks // -10)
    links = []
    if pagesToGet < 1:
        return []
    if pagesToGet >= 100:
        logging.root.warning("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    for page in range(pagesToGet):
        params = {'q': keyPhrase, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page, 'fl': 'web_url'}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK':
            logging.root.warning(response.json()['errors'][0])
            continue
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']:
            logging.root.warning(f"Only {page-1} hits found, {pagesToGet} requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        links.extend([doc['web_url'] for doc in articles])
    return links


def getJSON(keyPhrase, numLinks, webdriverOptions=None):
    contents = []
    if numLinks < 1:
        return []
    pagesToGet = -(numLinks // -10)
    if pagesToGet >= 100:
        logging.root.warning("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    for page in range(pagesToGet):
        if page > 0: # Avoid API request limit
            time.sleep(12)
        logging.root.info(f"Getting page {page}")
        params = {'q': keyPhrase, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK':
            logging.root.warning(response.json()['errors'][0])
            continue
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']:
            logging.root.warning(f"Only {page-1} hits found, {pagesToGet} requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        contents.extend(articles)
    return contents

