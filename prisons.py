from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import requests
import time

# Initialize WebDriver
def init_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

# Function to download file
def download_file(url, folder):
    local_filename = os.path.join(folder, os.path.basename(url))
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded: {local_filename}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

# Scrape a single page
def scrape_page(driver, url, output_folder, downloaded_files):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']
        if href.endswith('.pdf'):
            full_url = f"https://www.bop.gov{href}" if href.startswith('/') else href
            if full_url not in downloaded_files:
                download_file(full_url, output_folder)
                downloaded_files.add(full_url)
    
    # Handle pagination by clicking the next page image
    try:
        next_page_img = driver.find_element(By.XPATH, "//img[@alt='Next Page']")
        if next_page_img:
            next_page_img.click()
            time.sleep(3)  # Wait for the next page to load
            scrape_page(driver, driver.current_url, output_folder, downloaded_files)
    except Exception as e:
        print(f"No more pages or error navigating to the next page: {e}")

def main():
    base_url = 'https://www.bop.gov/foia/foia_available_records.jsp#'
    output_folder = 'C:\\Users\\scoll\\OneDrive\\Documents\\FOIA\\DOJ\\Prisons'
    downloaded_files = set()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    print("Starting the FOIA page PDF downloader script...")
    
    driver = init_driver()
    try:
        scrape_page(driver, base_url, output_folder, downloaded_files)
    finally:
        driver.quit()
        print("Script execution completed.")

if __name__ == "__main__":
    main()
