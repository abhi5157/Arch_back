import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.cadblocksfree.com"
TARGET_PAGE = "/en/store/landscaping.html"
DOWNLOAD_DIR = "data/raw/blueprints"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def fetch_download_links():
    url = urljoin(BASE_URL, TARGET_PAGE)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    links = []
    for a in soup.find_all('a', href=True):
        if "/en/store/download/" in a['href']:
            links.append(urljoin(BASE_URL, a['href']))
    return links[:10]  # Limit to first 10 to avoid overloading

def download_cad_file(url):
    file_name = url.split("/")[-1] + ".zip"
    response = requests.get(url)
    path = os.path.join(DOWNLOAD_DIR, file_name)
    with open(path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {file_name}")

if __name__ == "__main__":
    links = fetch_download_links()
    for link in links:
        download_cad_file(link)
