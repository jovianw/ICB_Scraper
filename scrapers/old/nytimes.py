import os
import requests
import logging
import time

API_KEY = os.getenv('NYTimes_Key')

def getLinks(keyPhrase, numLinks, patience, webdriverOptions=None):
    if not API_KEY:
        logging.root.warning(f"No 'NYTimes_Key' environmental variable found. Need an API key to access NYTimes. Continuing...")
        return []
    # Calculate number of pages to get
    pagesToGet = -(numLinks // -10)
    links = []
    if pagesToGet < 1:
        return []
    if pagesToGet >= 100:
        logging.root.warning("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    # For each page
    for page in range(pagesToGet):
        logging.root.info(f"NYTimes: Getting new page...")
        params = {'q': keyPhrase, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page, 'fl': 'web_url'}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK': # If status is not OK
            logging.root.warning(response.json()['errors'][0])
            continue
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']: # If no more results
            logging.root.warning(f"Only {page-1} hits found, {pagesToGet} requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        links.extend([doc['web_url'] for doc in articles])
    return links


def getJSON(keyPhrase, numLinks, patience, webdriverOptions=None):
    if not API_KEY:
        logging.root.warning(f"No 'NYTimes_Key' environmental variable found. Need an API key to access NYTimes. Continuing...")
        return []
    contents = []
    if numLinks < 1:
        return []
    # Calculate pages to get
    pagesToGet = -(numLinks // -10)
    if pagesToGet >= 100:
        logging.root.warning("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    # For each page
    for page in range(pagesToGet):
        if page > 0: # Avoid API request limit
            time.sleep(12)
        logging.root.info(f"NYTimes: Getting new page...")
        params = {'q': keyPhrase, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK': # If status is not OK
            logging.root.warning(response.json()['errors'][0])
            continue
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']: # If no more results
            logging.root.warning(f"Only {page-1} hits found, {pagesToGet} requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        contents.extend(articles)
    return contents

