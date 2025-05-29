import os
import time
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError, HTTPError

# Base URL of the page containing the main links
base_url = "https://www.esd.whs.mil/FOIA/Reading-Room/Reading-Room-List_2/"
# Directory to save all the PDFs
base_download_dir = r"C:\Users\scoll\OneDrive\Documents\FOIA\DOD\ExecServicesDirectorate"

# Ensure the base download directory exists
os.makedirs(base_download_dir, exist_ok=True)

# Fetch the main page
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all main links that lead to the pages with PDFs
main_links = soup.find_all('a', href=True)

# Function to download a PDF file
def download_pdf(pdf_url, file_path):
    # Check if the file already exists
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}, skipping download.")
        return
    
    try:
        with requests.get(pdf_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {file_path}")
    except HTTPError as e:
        if e.response.status_code == 401:
            print(f"Failed to download {file_path} due to authorization error: {e}")
        else:
            print(f"Failed to download {file_path} from {pdf_url}: {e}")
    except OSError as e:
        print(f"Failed to save {file_path} due to OS error: {e}")
    except ConnectionError as e:
        print(f"Network error occurred while downloading {file_path}: {e}")

# Function to process each section starting from the specific link
def process_section(starting_point):
    start_processing = False
    for main_link in main_links:
        link_text = main_link.text.strip()
        
        # Start processing after encountering the specified starting link
        if link_text == starting_point:
            start_processing = True

        if not start_processing:
            continue

        main_url = main_link['href']

        # Handle relative URLs by making them absolute
        if not main_url.startswith('http'):
            main_url = f"https://www.esd.whs.mil{main_url}"

        # Create a folder name based on the link text, replacing spaces with underscores
        folder_name = link_text.replace(" ", "_")
        folder_path = os.path.join(base_download_dir, folder_name)

        # Ensure the directory for this section exists
        os.makedirs(folder_path, exist_ok=True)

        # Retry logic for fetching the subpage
        retries = 3
        for i in range(retries):
            try:
                # Fetch the subpage
                sub_response = requests.get(main_url)
                sub_response.raise_for_status()
                sub_soup = BeautifulSoup(sub_response.content, 'html.parser')
                break  # Exit the retry loop if successful
            except ConnectionError as e:
                print(f"Attempt {i+1} failed to reach {main_url}: {e}")
                time.sleep(5)  # Wait before retrying
            else:
                print(f"Failed to fetch {main_url} after {retries} retries.")
                continue  # Skip to the next main link

        # Find all PDF links on the subpage
        pdf_links = sub_soup.find_all('a', href=True)
        pdf_links = [link for link in pdf_links if '.pdf' in link['href'].lower()]

        # Download each PDF into the corresponding folder
        for link in pdf_links:
            pdf_url = link['href']

            # Handle relative URLs by making them absolute
            if not pdf_url.startswith('http'):
                pdf_url = f"https://www.esd.whs.mil{pdf_url}"

            # Clean the file name to remove query parameters and ensure it's valid
            file_name = pdf_url.split("/")[-1].split("?")[0]
            file_path = os.path.join(folder_path, file_name)

            download_pdf(pdf_url, file_path)

        print(f"Completed processing section: {link_text}")

# Specify the starting point
starting_point = "Acquisition, Budget and Financial Matters"

# Call the function to start processing from the specified link
process_section(starting_point)

print("All PDFs that could be downloaded have been processed.")
