import os
import requests
import json
import warnings
import pandas as pd
import time

API_KEY = os.getenv('NYTimes_Key')
keyword = "https://www.nytimes.com/2023/05/18/business/walmart-earnings-1q-2023.html"
pagesToGet= 5

def getLinks(keyword, pagesToGet):
    links = []
    if pagesToGet < 1:
        raise("Number of pages must be positive.")
    if pagesToGet >= 100:
        warnings.warn("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    for page in range(pagesToGet):
        params = {'q': keyword, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page, 'fl': 'web_url'}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK':
            warnings.warn(response.json()['errors'][0])
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']:
            warnings.warn("Only " + str(page-1) + " hits found, " + str(pagesToGet) + " requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        links.extend([doc['web_url'] for doc in articles])
    return links


# links = getLinks(keyword, pagesToGet)
# print(links)
# print(len(links))
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('data/nytimes_links.csv', index=False)


def getContent(keyword, pagesToGet, verbose=0):
    contents = []
    if pagesToGet < 1:
        raise("Number of pages must be positive.")
    if pagesToGet >= 100:
        warnings.warn("Too many pages requested, should be <100")
        pagesToGet = 100
    url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
    for page in range(pagesToGet):
        if page > 0: # Avoid API request limit
            time.sleep(12)
        if verbose == 1:
            print("Getting page", page)
        params = {'q': keyword, 'api-key': API_KEY, 'type_of_material.contains': 'Text', 'page': page}
        response = requests.get(url, params=params)
        if response.json()['status'] != 'OK':
            warnings.warn(response.json()['errors'][0])
        if response.json()['response']['meta']['offset'] > response.json()['response']['meta']['hits']:
            warnings.warn("Only " + str(page-1) + " hits found, " + str(pagesToGet) + " requested. Exiting.")
            break
        articles = response.json()['response']['docs']
        contents.extend([{'Headline': doc['headline']['main'], 'Description': doc['abstract'], 'Content': doc['lead_paragraph']} for doc in articles])
    return contents

contents = getContent(keyword, pagesToGet, 1)
df = pd.DataFrame(contents)
df.to_csv('data/nytimes_contents.csv', index=False)