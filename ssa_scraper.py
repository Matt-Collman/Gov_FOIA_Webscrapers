import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to geckodriver
geckodriver_path = r"C:\Users\scoll\Downloads\geckodriver-v0.34.0-win64\geckodriver.exe"
service = Service(executable_path=geckodriver_path)

# Set up Firefox WebDriver
driver = webdriver.Firefox(service=service)

# Base URL
base_url = "https://www.ssa.gov"

# Open the SSA FOIA Reading Room page
driver.get("https://www.ssa.gov/foia/readingroom.html")

# Wait for the Proactive Disclosures dropdown to be clickable
proactive_disclosures = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "js-al-0"))
)

# Click the Proactive Disclosures dropdown to expand it
proactive_disclosures.click()

# Wait for the links within the dropdown to be visible
download_links = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='proactivedisclosure']"))
)

# Directory to save the downloaded files
download_dir = r"C:\Users\scoll\OneDrive\Documents\FOIA\SSA"

# Ensure the download directory exists
os.makedirs(download_dir, exist_ok=True)

# Function to download a file
def download_file(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download {file_path}: {response.status_code}")

# Iterate over the download links and download each file
for link in download_links:
    relative_url = link.get_attribute('href')
    if relative_url:
        # Ensure the relative URL is correctly appended to the base URL
        if relative_url.startswith('/'):
            full_url = base_url + relative_url
        else:
            full_url = relative_url

        print(f"Attempting to download: {full_url}")  # Print the URL being attempted
        file_name = full_url.split('/')[-1]
        file_path = os.path.join(download_dir, file_name)
        
        try:
            download_file(full_url, file_path)
        except Exception as e:
            print(f"Failed to download {file_name}: {e}")

# Close the WebDriver
driver.quit()
