import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd
from typing import Dict, Optional

class ProfileScraper:
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"):
        self.headers = {"User-Agent": user_agent}

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch URL and return BeautifulSoup object with error handling."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'lxml')
            else:
                print(f"Error fetching {url}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception fetching {url}: {e}")
            return None

    def scrape_github(self, username: str) -> Dict[str, str]:
        """Scrape GitHub profile for bio, company, website, and email."""
        url = f"https://github.com/{username}"
        soup = self._get_soup(url)
        data = {"bio": "", "company": "", "website": "", "email": ""}
        
        if not soup:
            return data
            
        # Get Bio
        bio_div = soup.select_one(".p-note.user-profile-bio")
        if bio_div:
            data["bio"] = bio_div.get_text(strip=True)
            
        # Get Company
        company_span = soup.select_one(".p-org")
        if company_span:
            data["company"] = company_span.get_text(strip=True)
            
        # Get Website
        website_link = soup.select_one("[itemprop='url']")
        if website_link:
             data["website"] = website_link.get_text(strip=True)
             
        # Get Email (if public)
        email_link = soup.select_one(".Link--primary[href^='mailto:']")
        if email_link:
            data["email"] = email_link.get_text(strip=True)
            
        # Fallback: check bio for email if not found in specific field
        if not data["email"]:
            email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", data["bio"])
            if email_match:
                data["email"] = email_match.group(0)
                
        return data

    def scrape_dev(self, username: str) -> Dict[str, str]:
        """Scrape DEV.to profile for bio and website."""
        url = f"https://dev.to/{username}"
        soup = self._get_soup(url)
        data = {"bio": "", "company": "", "website": "", "email": ""}
        
        if not soup:
            return data
            
        # Bio
        bio_el = soup.select_one(".profile-header__bio")
        if bio_el:
            data["bio"] = bio_el.get_text(strip=True)
            
        # Website/Links
        link_els = soup.select(".profile-header__links a")
        for link in link_els:
            href = link.get("href", "")
            if "mailto:" in href:
                data["email"] = href.replace("mailto:", "").strip()
            elif "github.com" not in href and "twitter.com" not in href:
                # Assuming other links might be his website
                data["website"] = href
                
        return data

    def scrape_medium(self, username: str) -> Dict[str, str]:
        """Scrape Medium profile for bio."""
        # Medium handles are usually @username
        handle = username if username.startswith("@") else f"@{username}"
        url = f"https://medium.com/{handle}"
        soup = self._get_soup(url)
        data = {"bio": "", "company": "", "website": "", "email": ""}
        
        if not soup:
            return data
            
        # Medium often puts bio in og:description or a specific tag
        meta_desc = soup.find("meta", property="og:description")
        if meta_desc:
            data["bio"] = meta_desc.get("content", "").strip()
            
        # Emails in bio
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", data["bio"])
        if email_match:
            data["email"] = email_match.group(0)
            
        return data

    def enrich_csv(self, input_file: str, output_file: str):
        """Read CSV, enrich with profile data, and save."""
        df = pd.read_csv(input_file)
        
        # Add new columns
        for col in ["bio", "company", "website", "email"]:
            if col not in df.columns:
                df[col] = ""
        
        print(f"Enriching {len(df)} leads from {input_file}...")
        
        for idx, row in df.iterrows():
            platform = str(row.get("platform", "")).lower()
            username = str(row.get("username", ""))
            
            if not username or username == "nan":
                continue
                
            profile_data = None
            if "github" in platform:
                profile_data = self.scrape_github(username)
            elif "dev" in platform:
                profile_data = self.scrape_dev(username)
            elif "medium" in platform:
                profile_data = self.scrape_medium(username)
                
            if profile_data:
                for key, val in profile_data.items():
                    if val:
                        df.at[idx, key] = val
                
                # Sleep to be nice
                time.sleep(random.uniform(0.5, 1.5))
                
            if (idx + 1) % 5 == 0:
                print(f"Processed {idx + 1}/{len(df)} leads...")
                
        df.to_csv(output_file, index=False)
        print(f"Enrichment completed. Saved to {output_file}")
