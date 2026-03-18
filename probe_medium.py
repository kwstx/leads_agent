import requests
from bs4 import BeautifulSoup

url = "https://medium.com/tag/ai"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Medium often uses 'article' tags
articles = soup.find_all('article')
print(f"Found {len(articles)} articles")

for article in articles[:5]:
    # Medium structure changes often, but titles are usually in h2 or h3
    title_tag = article.find('h2') or article.find('h3')
    title = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    # Try to find the link
    link_tag = article.find('a', href=True)
    link = link_tag['href'] if link_tag else "No Link"
    if link.startswith('/'):
        link = "https://medium.com" + link
    
    # Author is usually in a specific span or link
    # This is a guestimate
    author = "Unknown"
    for a in article.find_all('a'):
        if '/@' in a.get('href', ''):
            author = a.get_text(strip=True)
            break
            
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Link: {link}")
    print("-" * 10)
