import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv
import time
import json
from bs4.element import Tag
import numpy as np

output = './output.csv' 
with open(output, 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['category', 'title', 'date', 'author', 'summary', 'content', 'tags'])

def get_text(soup): 
    txt = ''
    for par in soup.find_all(lambda tag:tag.name=="p" and not "Related:" in tag.text):
        txt += ' ' + re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',par.get_text())
    return txt.strip()

def prepare_pandas(df):
    df.index = df.date
    df.drop(columns = 'date', inplace = True)
    df.index = pd.to_datetime(df.index, utc = True)
    df.sort_index(inplace = True)
    return df

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 91.0.4472.124 Safari/537.36'}

url_base = "https://cointelegraph.com/post-sitemap-"
total_posts = 0

bad_response = []
bad_response_count = 0

unparsable_webpage = []


def get_pages(headers):
    sitemap_url = 'https://cointelegraph.com/sitemap.xml'
    sitemap_webpage = requests.get(sitemap_url, headers=headers)
    sitemap_soup = BeautifulSoup(sitemap_webpage.text, features='xml')
    sitemap_all_links = sitemap_soup.find_all('loc')
    
    sitemap_pages = [link.getText() for link in sitemap_all_links if 'post-' in link.getText() and link.getText().endswith('.xml')]
    
    agg_pages = max([int(a.split('-')[-1].replace('.xml', '')) for a in sitemap_pages])

    return agg_pages 


def main():
    pages = get_pages(headers)

    for i in range(1, pages+1): 
        url = url_base+str(i)
        print('scraping ', url)
        web_map = requests.get(url, headers = headers)
        soup = BeautifulSoup(web_map.text, features = 'lxml')

        all_links = soup.find_all('loc')

        posts_downloaded = 0
        
        for item in all_links:

            url_post = item.getText()

            is_news = url_post.split('/')[3]
            
            if is_news != "news":
                print('\n')
                print(is_news, 'not a news item \n')
                continue
            
            page = requests.get(url_post, headers = headers)
            page.encoding = 'utf-8'
            sauce = BeautifulSoup(page.text,"lxml")
            
            try:
                data = json.loads(sauce.find('script', type='application/ld+json').string)
            except:
                print('Something is wrong: status', page.status_code, 'will sleep and retry')
                time.sleep(4)
                try: 
                    data = json.loads(sauce.find('script', type='application/ld+json').string)
                except:
                    print('Sleeping didnt solve the problem, going to the next post')
                    bad_response.append(url_post)
                    bad_response_count +=1
                    continue
                    
                
            try:
                art_tag = data['articleSection']    
            except: 
                art_tag = None
            try:
                date = data['datePublished']
            except:
                date = None
                
            titleTag = sauce.find("h1",{"class":"post__title"})
            authorTag = sauce.find("div", {"class":"post-meta__author-name"})
            summaryTag = sauce.find("p", {"class":"post__lead"})
            contentTag = sauce.find("div",{"class":"post-content"})
            tagsTag = sauce.find('ul', {"class":"tags-list__list"}) # classification tags 
            
            title = None
            author = None
            content = None
            summary = None
            tags_list = None
            
            if isinstance(titleTag,Tag):
                title = titleTag.get_text().strip()
                print(title)

            if isinstance(authorTag, Tag):
                author = authorTag.get_text().strip()
            
            if isinstance(contentTag,Tag):
                content = get_text(contentTag)
        
            if isinstance(summaryTag, Tag):
                summary = summaryTag.get_text().strip() 
                
            if isinstance(tagsTag, Tag):
                tags_str = tagsTag.get_text().strip()
                tags_list_prep = tags_str.split('#')
                tags_list = [i.strip() for i in tags_list_prep if len(i)>0]
                
                    
            with open(output, 'a', encoding = 'utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([art_tag, title, date, author, summary, content, tags_list])
                
            posts_downloaded +=1
            
        total_posts += posts_downloaded
        print('loaded ', total_posts, 'posts')
           
        
    news_map = pd.read_csv(output)
    news_map = prepare_pandas(news_map)


if __name__ == "__main__":
    main()

