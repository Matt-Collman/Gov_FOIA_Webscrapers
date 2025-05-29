from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import os
import requests
import time

# Initialize WebDriver with Firefox
gecko_path = 'C:/Users/scoll/downloads/geckodriver-v0.34.0-win64/geckodriver.exe'
service = Service(gecko_path)
firefox_options = Options()
firefox_options.add_argument("--headless")
driver = webdriver.Firefox(service=service, options=firefox_options)

# Base URL
base_url = 'https://cops.usdoj.gov'
driver.get(f'{base_url}/programdocuments')

# Wait for page to load
time.sleep(5)

# Create base directory
base_directory = 'C:/Users/scoll/OneDrive/Documents/FOIA/DOJ/COPS'
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

print("Base directory created:", base_directory)

# Find and iterate through each year section header
years = driver.find_elements(By.XPATH, "//h2")
print("Found years:", len(years))
for year in years:
    year_text = year.text.strip()
    year_directory = os.path.join(base_directory, year_text)
    
    if not os.path.exists(year_directory):
        os.makedirs(year_directory)
    
    print("Year directory created:", year_directory)
    
    # Find all categories within the year
    categories = year.find_elements(By.XPATH, ".//following-sibling::div[@class='accordion']//div[@class='accordion-section']")
    print(f"Found categories for {year_text}:", len(categories))
    for category in categories:
        category_title_element = category.find_element(By.XPATH, ".//a[contains(@class, 'accordion-section-title')]")
        category_title = category_title_element.text.strip().replace(' ', '_')
        category_directory = os.path.join(year_directory, category_title)
        
        if not os.path.exists(category_directory):
            os.makedirs(category_directory)
        
        print("Category directory created:", category_directory)
        
        # Expand the category section
        category_title_element.click()
        time.sleep(1)
        
        # Find all PDF links within the category
        pdf_links = category.find_elements(By.XPATH, ".//a[contains(@href, '.pdf')]")
        print(f"Found PDF links in category {category_title}:", len(pdf_links))
        for link in pdf_links:
            pdf_url = link.get_attribute('href')
            pdf_name = pdf_url.split('/')[-1]
            pdf_path = os.path.join(category_directory, pdf_name)
            
            # Download the PDF
            try:
                response = requests.get(pdf_url)
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                print(f'Downloaded: {pdf_path}')
            except Exception as e:
                print(f'Failed to download {pdf_url}: {e}')
        
        # Collapse the category section
        category_title_element.click()
        time.sleep(1)

driver.quit()
print("Script execution completed.")
