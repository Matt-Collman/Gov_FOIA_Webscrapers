from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import os
import time

# Set up the WebDriver for Firefox using Geckodriver
geckodriver_path = r"C:\Users\scoll\Downloads\geckodriver-v0.34.0-win64\geckodriver.exe"
service = Service(executable_path=geckodriver_path)
driver = webdriver.Firefox(service=service)

# URL to scrape
base_url = "https://www.rmda.army.mil/readingroom/index.aspx"
driver.get(base_url)

# Give the page time to load
time.sleep(5)  # You might need to adjust this based on your connection

# Define the base download folder
download_base = r"C:\Users\scoll\OneDrive\Documents\FOIA\DOD\Army"

# Get a list of all section links in the main body
sections = driver.find_elements(By.CSS_SELECTOR, ".colwrapper a.listSize")

for i, section in enumerate(sections):
    try:
        # Re-locate the section element to avoid StaleElementReferenceException
        sections = driver.find_elements(By.CSS_SELECTOR, ".colwrapper a.listSize")
        section = sections[i]
        section_name = section.text.replace(" ", "_")
        folder_path = os.path.join(download_base, section_name)

        # Create directory for the section
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Click on the section link
        section.click()

        # Wait for the page to load (adjust the sleep time as necessary)
        time.sleep(5)

        # Download all PDFs and MP3s
        download_links = driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf'], a[href$='.mp3']")
        for link in download_links:
            file_url = link.get_attribute('href')
            file_name = os.path.join(folder_path, os.path.basename(file_url))
            
            # Download the file
            try:
                driver.get(file_url)
                with open(file_name, 'wb') as file:
                    file.write(driver.page_source.encode('utf-8'))
                print(f"Downloaded {file_name}")
            except Exception as e:
                print(f"Failed to download {file_name}: {str(e)}")
        
        # Go back to the main page
        driver.back()
        time.sleep(5)  # Wait for the main page to reload

    except StaleElementReferenceException:
        print(f"StaleElementReferenceException encountered. Skipping section: {section_name}")
        continue

# Close the WebDriver
driver.quit()
