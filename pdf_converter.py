import os
import requests
import base64
from PyPDF2 import PdfReader

# Set your WordPress site details
WP_URL = 'http://foiarchive/wp-json/wp/v2'
WP_USER = 'Matt'
WP_PASSWORD = 'Aak98011#'
UPLOAD_DIR = 'C:\\Users\\scoll\\OneDrive\\Documents\\FOIA\\cia'
CATEGORY_ID = 8 # Replace with the actual category ID

# Encode credentials
credentials = f"{WP_USER}:{WP_PASSWORD}"
token = base64.b64encode(credentials.encode())
headers = {
    'Authorization': f'Basic {token.decode("utf-8")}',
}

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page in range(num_pages):
            text += reader.pages[page].extract_text() or ""
    return text

def upload_pdf_to_wordpress(pdf_path):
    # Upload PDF to WordPress Media Library
    with open(pdf_path, 'rb') as file:
        filename = os.path.basename(pdf_path)
        files = {
            'file': (filename, file, 'application/pdf')
        }
        response = requests.post(f"{WP_URL}/media", headers=headers, files=files)
        
        if response.status_code != 201:
            print(f"Failed to upload {filename}: {response.status_code}, {response.text}")
            return None
        
        try:
            media_data = response.json()
            return media_data['source_url']  # Return the URL of the uploaded PDF
        except requests.exceptions.JSONDecodeError:
            print(f"Failed to decode JSON response for {filename}")
            return None

def create_wordpress_page(title, content, pdf_url, category_id):
    # Ensure headers are set for JSON
    json_headers = headers.copy()
    json_headers['Content-Type'] = 'application/json'

    # Create a new page on WordPress
    post = {
        'title': title,
        'content': f"{content}<br/><a href='{pdf_url}'>Download PDF</a>",
        'status': 'publish',
        'categories': [CATEGORY_ID],  # Assign the post to the specified category
    }
    response = requests.post(f"{WP_URL}/pages", headers=json_headers, json=post)
    
    if response.status_code not in [200, 201]:
        print(f"Failed to create page {title}: {response.status_code}, {response.text}")
        return None
    
    return response.json()

def process_pdfs_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                try:
                    text = extract_text_from_pdf(pdf_path)
                    print(f"Extracted text from {filename}")
                    pdf_url = upload_pdf_to_wordpress(pdf_path)
                    if pdf_url:
                        create_wordpress_page(filename, text, pdf_url, CATEGORY_ID)
                        print(f"Created post for {filename}")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
# Process all PDFs in the folder
process_pdfs_in_folder(UPLOAD_DIR)
