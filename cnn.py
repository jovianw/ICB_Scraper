
import urllib.request,sys,time
from bs4 import BeautifulSoup
import requests
import pandas as pd
from selenium import webdriver

keyword = "Walmart"
pagesToGet= 5


def getLinks(keyword, pagesToGet):
    browser = webdriver.Chrome()
    links = []

    for page in range(1, pagesToGet + 1):
        print('processing page :', page)
        url = "https://www.cnn.com/search?q=" + keyword + "&from=" + str(50 * (page - 1)) + "&size=50&page=" + str(page) + "&sort=relevance&types=all&section="
        print(url)
        
        #an exception might be thrown, so the code should be in a try-except block
        try:
            #use the browser to get the url. This is suspicious command that might blow up.
            browser.get(url)
        except Exception as e:
            error_type, error_obj, error_info = sys.exc_info()
            print ('ERROR FOR LINK:', url)
            print (error_type, 'Line:', error_info.tb_lineno)
            continue #ignore this page. Abandon this and go back.
        time.sleep(2)   
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for article in soup.find_all(class_='container__link'):
            links.append(article.get('href'))

    return links


# links = getLinks(keyword, pagesToGet)
# df = pd.DataFrame(links, columns=['URL'])
# df.to_csv('cnn_links.csv', index=False)


def getContent(links):
    def isContent(tag):
        if tag.has_attr('id') and tag['id'] == 'storytext':
            return True
        if tag.has_attr('class') and 'article__content' in tag['class']:
            return True
        return False

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    browser = webdriver.Chrome(chrome_options=options)
    contents = []
    
    count = 0
    totalCount = len(links)
    for link in links:
        count += 1
        print(f'Processing article {count}/{totalCount}')

        # filter out video articles
        if "cnn.com/videos" in link:
            continue
        
        print("making connection")
        try:
            #use the browser to get the url. This is suspicious command that might blow up.
            browser.get(link)
        except Exception as e:
            error_type, error_obj, error_info = sys.exc_info()
            print ('ERROR FOR LINK:', link)
            print (error_type, 'Line:', error_info.tb_lineno)
            continue #ignore this page. Abandon this and go back.
        print("waiting")
        time.sleep(2)   
        print("getting html")
        html = browser.page_source
        print("making soup")
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup.get_text())
        print("getting headline")
        headlineDiv = soup.find('h1', class_=['article-title', 'headline__text'])
        if headlineDiv: 
            headline = headlineDiv.string.strip()
        else:
            headline = ""
        print("getting content")
        content = ""
        contentDiv = soup.find(isContent)
        if contentDiv:
            for paragraph in contentDiv.find_all('p'):
                content += "".join(paragraph.strings)
        contents.append({'Headline': headline, 'Content': content})
    print('done')
    return contents


df = pd.read_csv('data/cnn_links.csv')
links = df['URL'].values.tolist()
contents = getContent(links)
df = pd.DataFrame(contents)
df.to_csv('data/cnn_contents.csv', index=False)
    