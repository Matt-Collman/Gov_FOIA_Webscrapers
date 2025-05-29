import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Set the base URL and the destination folder
base_url = 'https://www.cia.gov/readingroom/home'
base_readingroom_url = 'https://www.cia.gov/readingroom/'
destination_folder = 'C:\\Users\\scoll\\OneDrive\\Documents\\FOIA\\CIA'
visited_urls = set()  # Keep track of visited URLs to avoid loops
max_depth = 3  # Set a maximum depth for recursion to avoid deep nesting

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Function to create a folder based on a URL
def create_folder_for_url(url, base_folder):
    path = urlparse(url).path.strip('/').replace('/', '_')
    folder_path = os.path.join(base_folder, path)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# Function to download a file
def download_file(file_url, destination_folder):
    local_filename = os.path.join(destination_folder, file_url.split('/')[-1])
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

# Function to recursively find and download PDFs
def find_and_download_pdfs(url, base_folder, depth=0):
    if url in visited_urls or depth > max_depth:
        return
    
    visited_urls.add(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Create a folder for the current URL
    current_folder = create_folder_for_url(url, base_folder)
    
    # Find all links on the page
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        full_url = urljoin(url, href)
        
        # Check if the link points to a PDF
        if full_url.endswith('.pdf'):
            print(f"Downloading {full_url}")
            try:
                download_file(full_url, current_folder)
                print(f"Downloaded: {full_url} into {current_folder}")
            except Exception as e:
                print(f"Failed to download {full_url}: {e}")
        
        # Check if the link points to another page under the reading room
        elif full_url.startswith(base_readingroom_url) and not full_url.endswith('.pdf'):
            find_and_download_pdfs(full_url, base_folder, depth + 1)

# Start the process
find_and_download_pdfs(base_url, destination_folder)

print("All PDFs downloaded.")
