import requests
from bs4 import BeautifulSoup
import re
import time
import csv

# NOTE: Below Benzinga Sitemap appears to be out of date and no longer in use. Only contains small set of articles.

storage_file = './data/test.csv'

url_base = "https://www.benzinga.com/sitemap.xml?page="
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 91.0.4472.124 Safari/537.36'}

def get_urls_from_sitemap(sitemap_url, headers):
    response = requests.get(sitemap_url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')
    article_urls = [loc.get_text() for loc in soup.find_all('loc')]
    return article_urls

def filter_articles(article_urls):
    return [url for url in article_urls if '/markets/cryptocurrency/' in url]

def prepare_pandas(df):
    df.index = df.date
    df.drop(columns = 'date', inplace = True)
    df.index = pd.to_datetime(df.index, utc = True)
    df.sort_index(inplace = True)
    return df



def main():
    total_posts = 0
    bad_response_count = 0
    pages = 6  # Benzinga Sitemap only contains 6 pages 

    for i in range(1, pages + 1):
        sitemap_url = f"{url_base}{i}"
        print(f'Scraping {sitemap_url}')
        article_urls = get_urls_from_sitemap(sitemap_url, headers)
        crypto_article_urls = filter_articles(article_urls)

        for url_post in crypto_article_urls:
            try:
                page = requests.get(url_post, headers=headers)
                if page.status_code == 200:
                    soup = BeautifulSoup(page.content, 'lxml')
                    soup_html = BeautifulSoup()

                    # Title
                    title_tag = soup.find('h1', class_='sc-fHekdT ksRSID layout-title').get_text(strip=True)

                    #publish Date
                    article_date = soup.find('span', class_='date').get_text(strip=True)

                    #Author 
                    author_tag = soup.find('a', class_='author-name')
                    author_name = author_tag.get_text(strip=True)
                    # print(author_name)

                    # Article Content
                    core_blocks = soup.find_all('p', class_='block core-block')
                    all_core_block_text = ' '.join(block.get_text(separator=" ", strip=True) for block in core_blocks)
                    # Tags
                    tags_class = "article-taxonomy"
                    article_tags_div = soup.find('div', class_=tags_class)
                    tags_text = [a.get_text(strip=True) for a in article_tags_div.find_all('a')]

                    with open(storage_file, 'a', encoding = 'utf-8') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([title_tag, article_date, author_name, all_core_block_text, tags_text])

                    total_posts += 1
                else:
                    print(f'Bad response for {url_post}')
                    bad_response_count += 1
            except Exception as e:
                print(f'Error processing {url_post}: {e}')
                bad_response_count += 1
            time.sleep(1) 

    print(f'Total cryptocurrency articles processed: {total_posts}')
    print(f'Total bad responses: {bad_response_count}')
    news_map = pd.read_csv(storage_file)
    news_map = prepare_pandas(news_map)



if __name__ == "__main__":
    main()

