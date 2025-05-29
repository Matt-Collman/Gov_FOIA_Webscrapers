import requests
import base64
import os
import fitz  # PyMuPDF for PDF extraction
import pytesseract  # For OCR on scanned PDFs
from pdf2image import convert_from_path  # To convert PDF pages to images

# WordPress API credentials
wp_user = "Matt"
wp_password = "Aak98011#"
wp_base_url = "http://foiarchive/wp-json/wp/v2/"

# Create an API token using the username and password
credentials = f"{wp_user}:{wp_password}"
token = base64.b64encode(credentials.encode())

headers = {
    "Authorization": f"Basic {token.decode('utf-8')}",
    "Content-Type": "application/json"
}

# Set the parent page ID (for "12 Oxcart Reconnaissance Aircraft Documentation")
parent_page_id = 114

def create_wordpress_page(title, content, parent_id):
    post = {
        "title": title,
        "content": content,
        "status": "publish",  # You can use 'draft' if you don't want it published right away
        "parent": parent_id  # Set the parent page ID
    }

    # Send the POST request to create the new page
    response = requests.post(f"{wp_base_url}pages", json=post, headers=headers)

    if response.status_code == 201:
        print(f"Page created successfully: {response.json()['link']}")
    else:
        print(f"Failed to create page: {response.status_code}, {response.text}")

# Function to process a PDF and extract text/images
def process_pdf(file_path):
    pdf_document = fitz.open(file_path)
    pdf_text = ""

    # Loop through pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)

        # Extract text from the page
        text = page.get_text("text")
        if not text.strip():
            # If no text is found, treat it as a scanned PDF and apply OCR
            images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)
            for image in images:
                # Perform OCR on the image
                ocr_text = pytesseract.image_to_string(image)
                pdf_text += ocr_text + "\n"
        else:
            pdf_text += text + "\n"

    return pdf_text

# Generate HTML from extracted text (replacing newlines with <br> tags for readability)
def generate_html(content, title="Document Title"):
    html_content = """
    <html>
    <head>
        <title>{}</title>
    </head>
    <body>
        <h1>{}</h1>
        <p>{}</p>
    </body>
    </html>
    """.format(title, title, content.replace('\n', '<br>'))
    
    return html_content

# Process and publish PDFs as new pages on WordPress
def process_and_publish_pdfs(pdf_folder):
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            
            # Remove the ".pdf" extension to get the title
            title = os.path.splitext(filename)[0]

            # Process the PDF to extract text using OCR if necessary
            extracted_text = process_pdf(file_path)
            
            # Generate HTML from the extracted text
            html_content = generate_html(extracted_text, title=title)
            
            # Create a new page on WordPress with the title and parent ID
            create_wordpress_page(title=title, content=html_content, parent_id=parent_page_id)

# Set the source folder for PDFs
pdf_folder = r"C:\Users\scoll\OneDrive\Documents\FOIA\CIA\readingroom_collection_12-oxcart-reconnaissance-aircraft-documentation"

# Run the process on your folder of PDFs
process_and_publish_pdfs(pdf_folder)
