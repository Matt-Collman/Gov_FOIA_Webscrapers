import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import re
import sys

BASE_URL = "https://www.dhs.gov/foia-library"
DOWNLOAD_DIR = r"C:\Users\scoll\OneDrive\Documents\FOIA\DHS"

def get_soup(url):
    print(f"Fetching URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully fetched {url}")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_accordion_menus(soup):
    menus = soup.find_all('div', class_='usa-accordion')
    print(f"Found {len(menus)} accordion menus")
    if not menus:
        print("No accordion menus found. The page structure might have changed.")
        print("Page content:", soup.prettify())
    return menus

def extract_pdf_links(url):
    soup = get_soup(url)
    if not soup:
        return []
    links = []
    for row in soup.find_all('tr'):
        link = row.find('a', href=lambda href: href and href.endswith('.pdf'))
        if link:
            title = link.text.strip()
            pdf_url = urljoin(url, link['href'])
            tds = row.find_all('td')
            file_type = tds[0].text.strip() if len(tds) > 0 else "Unknown"
            file_size = tds[1].text.strip() if len(tds) > 1 else "Unknown"
            date = tds[2].text.strip() if len(tds) > 2 else "Unknown"
            links.append((title, pdf_url, file_type, file_size, date))
    print(f"Found {len(links)} PDF links at {url}")
    return links

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_file(url, filepath):
    try:
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded: {filepath}")
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")

def main():
    print("Starting the scraping process...")
    max_files = 1000  # Initialize max_files here
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    soup = get_soup(BASE_URL)
    if not soup:
        print("Failed to fetch the main page. Exiting.")
        return

    menus = parse_accordion_menus(soup)
    if not menus:
        print("No menus found. Exiting.")
        return

    print(f"Processing {len(menus)} accordion menus.")
    
    file_count = 0
    for menu in menus:
        category = menu.find('button', class_='usa-accordion__button')
        if category:
            category = category.text.strip()
        else:
            print("Could not find category name. Skipping.")
            continue
        print(f"Processing category: {category}")
        category_dir = os.path.join(DOWNLOAD_DIR, category)
        os.makedirs(category_dir, exist_ok=True)

        content = menu.find('div', class_='usa-accordion__content')
        if not content:
            print(f"No content found for category {category}. Skipping.")
            continue
        links = content.find_all('a')
        
        for link in links:
            subcategory = link.text.strip()
            subcategory_url = urljoin(BASE_URL, link['href'])
            print(f"Fetching subcategory: {subcategory}")
            
            pdf_links = extract_pdf_links(subcategory_url)
            print(f"Found {len(pdf_links)} PDF links in {subcategory}")
            
            for title, url, file_type, file_size, date in pdf_links:
                safe_title = sanitize_filename(title)
                safe_date = sanitize_filename(date)
                filename = f"{safe_title}_{safe_date}.pdf"
                filepath = os.path.join(category_dir, filename)
                
                if not os.path.exists(filepath):
                    print(f"Downloading: {title}")
                    download_file(url, filepath)
                    file_count += 1
                    
                    if file_count >= max_files:
                        if input(f"Reached {max_files} files. Continue? (y/n): ").lower() != 'y':
                            return
                        max_files += 1000
                
                time.sleep(1)  # Be nice to the server

    print(f"Scraping completed. Total files downloaded: {file_count}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()