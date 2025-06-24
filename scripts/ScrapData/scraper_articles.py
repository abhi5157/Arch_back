# scraper.py
import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from urllib.parse import urljoin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "../data/raw")
os.makedirs(RAW_DIR, exist_ok=True)

def get_article_links(base_url, keyword_filter="architecture"):
    print(f"Fetching article links from: {base_url}")
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if keyword_filter in href and full_url not in links:
            links.append(full_url)

    return list(set(links))

def fetch_and_save_articles(links, source_name="source"):
    for i, url in enumerate(links):
        try:
            article = Article(url)
            article.download()
            article.parse()
            if article.text.strip():
                file_path = os.path.join(RAW_DIR, f"{source_name}_{i}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(article.title + "\n\n" + article.text)
                print(f"[✓] Saved: {file_path}")
        except Exception as e:
            print(f"[!] Failed to fetch {url}: {e}")

if __name__ == "__main__":
    # Example architecture blogs or news
    sources = {
        "archdaily": "https://www.archdaily.com",
        "designboom": "https://www.designboom.com/architecture/",
    }

    for name, base_url in sources.items():
        links = get_article_links(base_url)
        fetch_and_save_articles(links, source_name=name)

