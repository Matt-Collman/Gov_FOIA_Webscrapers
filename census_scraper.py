import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set your target URL and destination folder
url = 'https://www.census.gov/about/policies/foia/foia_library/frequently_requested_records.html'
destination_folder = 'C:\\Users\\scoll\\OneDrive\\Documents\\FOIA\\Census Bureau'

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Function to download a file
def download_file(file_url, destination_folder):
    local_filename = os.path.join(destination_folder, file_url.split('/')[-1])
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

# Fetch the page
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links that end with .pdf
pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))

# Download each PDF
for link in pdf_links:
    pdf_url = urljoin(url, link['href'])
    print(f"Downloading {pdf_url}")
    try:
        download_file(pdf_url, destination_folder)
        print(f"Downloaded: {pdf_url}")
    except Exception as e:
        print(f"Failed to download {pdf_url}: {e}")

print("All PDFs downloaded.")
