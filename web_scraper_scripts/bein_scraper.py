import requests
import pandas as pd
from bs4 import BeautifulSoup, NavigableString

import re
import csv
import time
import json
from bs4.element import Tag
import numpy as np

storage_file = './data/bein_output.csv' 

def extract_article_urls_from_xml_sitemap(sitemap_url, headers):
    response = requests.get(sitemap_url, headers=headers)
    if response.status_code == 200:
         soup = BeautifulSoup(response.content, 'xml')
         urls = []
         for url in soup.find_all('url'):
             loc = url.find('loc')
             if loc and not loc.find_parent('image:image'):
                 urls.append(loc.text)
         return urls
    else:
         print(f"failed to fetch the sitemap: {response.status_code}")
         return []
       
def main():
    with open(storage_file, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([ 'Title', 'Date', 'Author', 'Update Author', 'Content'])
    url_base = "https://beincrypto.com/wp-content/uploads/beincrypto-sitemaps/sitemap_index/post/sitemap"
    total_posts = 0

    bad_response = []
    bad_response_count = 0
    start_suffix = 312 
    end_suffix = 313 

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 91.0.4472.124 Safari/537.36'}
    unparsable_webpage = []
    
    for i in range(start_suffix, end_suffix + 1):
        page_url = f"{url_base}{i}.xml"
        print(page_url)
        article_urls = extract_article_urls_from_xml_sitemap(page_url, headers)
        for url in article_urls:
            try:
                response = requests.get(url, headers=headers)
                print(response.status_code)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    # TITLE
                    h1_element = soup.find('h1', class_="h4 lg:h1 mt-3 mb-2 lg:mb-3 w-full")
                    title_tag = h1_element.text.strip()
                    print(title_tag)
                    
                    # Author
                    author_element = soup.find('span', class_="text-blue-700 no-underline text-3")
                    author_tag = author_element.text.strip()
                    if author_tag == 'Advertorial':
                        updated_author = soup.find('a', class_="text-blue-700 no-underline ml-1 text-3")
                        update_tag = updated_author.text.strip()
                    else:
                        update_tag = None

                    print(author_tag)

                    # Date
                    date_element = soup.find('time')
                    if date_element:
                        attr = date_element['datetime']
                        print(attr)
                    else:
                        print("no time tag")

                    # CONTENT
                    content = soup.find('div', class_='entry-content-inner')
                    content_blocks = []
                    if content:
                        for child in content.children:
                            if child.name not in ['img', 'script', 'style']:
                                text = child.get_text(separator=' ', strip=True) if child.get_text else child
                                content_blocks.append(text)
                            elif child.name == 'div' and not child.has_attr('class'):
                                text = child.get_text(separator=' ', strip=True)
                                content_blocks.append(text)
                    full_text = ' '.join(content_blocks)
                    print(full_text)


                    with open(storage_file, 'a', encoding = 'utf-8') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow([title_tag, attr, author_tag, update_tag,  full_text])
                    total_posts += 1

            except Exception as e :
                print(f"error processing post: {e}")
                bad_response_count += 1

            time.sleep(5)

               



if __name__ == "__main__":
    main()
