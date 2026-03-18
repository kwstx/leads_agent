import requests
from bs4 import BeautifulSoup

url = "https://dev.to/t/ai/latest"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

articles = soup.find_all('div', class_='crayons-story')

print(f"Found {len(articles)} articles")

for article in articles[:5]:
    title_tag = article.find('h3', class_='crayons-story__title') or article.find('h2', class_='crayons-story__title')
    title = title_tag.get_text(strip=True) if title_tag else "No Title"
    
    link_tag = title_tag.find('a') if title_tag else None
    link = "https://dev.to" + link_tag['href'] if link_tag and link_tag.get('href', '').startswith('/') else link_tag.get('href') if link_tag else "No Link"
    
    author_tag = article.find('a', class_='crayons-story__author-name')
    author = author_tag.get_text(strip=True) if author_tag else "No Author"
    
    # Try different snippet containers
    snippet_tag = article.find('div', class_='crayons-story__description') or article.find('p', class_='crayons-story__snippet')
    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
    
    # Tags usually have a specific span or class
    tags = [tag.get_text(strip=True) for tag in article.find_all('span', class_='crayons-tag__name')]
    
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Link: {link}")
    print(f"Snippet: {snippet}")
    print(f"Tags: {tags}")
    print("-" * 10)
