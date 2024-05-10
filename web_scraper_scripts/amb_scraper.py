import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import pandas as pd


storage_path= './data/output.csv' 

sub_url = "https://www.ambcrypto.com/post-sitemap"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 91.0.4472.124 Safari/537.36'}

def get_article_urls_from_sitemap(sub_url, headers):
    """Fetches article URLs from a given sitemap URL."""
    response = requests.get(sub_url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    article_urls = [loc.get_text() for loc in soup.find_all('loc')]
    print(article_urls)
    return article_urls


def prepare_pandas(df):
    df.index = df.date
    df.drop(columns = 'date', inplace = True)
    df.index = pd.to_datetime(df.index, utc = True)
    df.sort_index(inplace = True)
    return df



def main():
    total_posts = 0
    bad_response_count = 0
    n_agg_pages = 28 

    for i in range(1, n_agg_pages + 1):
        sitemap_url = f"{sub_url}{i}.xml"
        print(f'Scraping {sitemap_url}')
        crypto_article_urls = get_article_urls_from_sitemap(sitemap_url, headers)

        for url_post in crypto_article_urls:
            try:
                page = requests.get(url_post, headers=headers)
                if page.status_code == 200:

                    soup = BeautifulSoup(page.content, 'lxml')
                    soup_html = BeautifulSoup()


                    # Title
                    title_tag = soup.find('h1', class_='post-title entry-title').get_text(strip=True)
                    print(title_tag)

                    #publish Date
                    article_date = soup.find('time', class_='post-date updated').get_text(strip=True)
                    print(article_date)
 #
 #                    #Author 
                    author_tag = soup.find('span', class_='author-name vcard fn author')
                    author_name = author_tag.get_text(strip=True)
                    print(author_name)
 #                    # print(author_name)
 #
                    # Article Content
                    core_blocks = soup.find_all('div', class_='single-post-main')
                    all_core_block_text = ' '.join(block.get_text(separator=" ", strip=True) for block in core_blocks)
                    print(all_core_block_text)

                    # write to csv file
                    with open(storage_path, 'a', encoding = 'utf-8') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([title_tag, article_date, author_name, all_core_block_text])

                    total_posts += 1
                else:
                    print(f'Bad response for {url_post}')
                    bad_response_count += 1
            except Exception as e:
                print(f'Error processing {url_post}: {e}')
                bad_response_count += 1
            time.sleep(0.2)  

    print(f'Total cryptocurrency articles processed: {total_posts}')
    print(f'Total bad responses: {bad_response_count}')
    news_map = pd.read_csv(storage_path)
    news_map = prepare_pandas(news_map)



if __name__ == "__main__":
    main()

