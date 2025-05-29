import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
import requests

# Configure logging
logging.basicConfig(filename='foia_download.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up the Selenium WebDriver for Firefox
firefox_options = Options()
 # Run in headless mode (no GUI)
service = Service(executable_path=r"C:\Users\scoll\Downloads\geckodriver-v0.34.0-win64\geckodriver.exe")

driver = webdriver.Firefox(service=service, options=firefox_options)

# Base URL and download directory
base_url = "https://www.dodig.mil/FOIA/FOIA-Reading-Room/"
download_dir = r"C:\Users\scoll\OneDrive\Documents\FOIA\DOD\IG"

# Ensure the download directory exists
os.makedirs(download_dir, exist_ok=True)

def download_pdf(pdf_url, file_name):
    file_path = os.path.join(download_dir, file_name)
    
    if os.path.exists(file_path):
        file_name = file_name.replace(".pdf", "_copy2.pdf")
        file_path = os.path.join(download_dir, file_name)

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(pdf_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                logging.info(f"Downloaded: {file_name}")
                return
            else:
                logging.error(f"Failed to download {file_name}, status code: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Error downloading {file_name}: {e}")
        time.sleep(2)  # Wait a bit before retrying

    logging.warning(f"Skipping {file_name} after 3 failed attempts")

def scrape_page(page_url):
    driver.get(page_url)
    time.sleep(2)  # Allow time for the page to load

    # Identify all subpage links that have 'Article' in the URL
    subpage_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/FOIA/FOIA-Reading-Room/Article/']")
    
    for i in range(len(subpage_links)):
        try:
            # Re-fetch the subpage links on each iteration to avoid stale elements
            subpage_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/FOIA/FOIA-Reading-Room/Article/']")
            subpage_url = subpage_links[i].get_attribute('href')
            logging.info(f"Scraping subpage: {subpage_url}")
            driver.get(subpage_url)
            time.sleep(2)

            try:
                pdf_links = driver.find_elements(By.CSS_SELECTOR, "a.link[href*='.pdf']")
                if pdf_links:
                    logging.info(f"Found {len(pdf_links)} PDF(s) on subpage: {subpage_url}")
                else:
                    logging.warning(f"No PDFs found on subpage: {subpage_url}")

                for pdf_link in pdf_links:
                    pdf_url = pdf_link.get_attribute('href')
                    file_name = pdf_url.split("/")[-1]
                    logging.info(f"Attempting to download PDF: {pdf_url}")
                    download_pdf(pdf_url, file_name)
            except NoSuchElementException:
                logging.warning(f"No PDF links found on subpage: {subpage_url}")
            except WebDriverException as e:
                logging.error(f"Error accessing PDF links on subpage {subpage_url}: {e}")

            # Go back to the main page after processing a subpage
            driver.back()
            time.sleep(2)

        except StaleElementReferenceException:
            logging.warning(f"Stale element encountered. Re-fetching the element.")
            continue

def main():
    try:
        for i in range(1, 39):  # Loop through pages 1 to 38
            page_url = f"{base_url}?Page={i}"
            logging.info(f"Processing page {i}")
            scrape_page(page_url)
        logging.info("Scraping completed.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
