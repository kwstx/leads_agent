import requests
from bs4 import BeautifulSoup

url = "https://medium.com/feed/tag/ai"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
# Parse with xml parser
soup = BeautifulSoup(response.text, 'xml') # BeautifulSoup(..., 'xml') is often better for RSS/XML

items = soup.find_all('item')
print(f"Found {len(items)} items in RSS feed")

for item in items[:3]:
    title = item.find('title').get_text(strip=True)
    link = item.find('link').get_text(strip=True)
    author = item.find('dc:creator').get_text(strip=True) if item.find('dc:creator') else "No Author"
    snippet = item.find('description').get_text(strip=True)[:200]
    categories = [cat.get_text() for cat in item.find_all('category')]
    
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Link: {link}")
    print(f"Snippet: {snippet}")
    print(f"Categories: {categories}")
    print("-" * 10)
