import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_pdf_links(url, visited_pages=None):
    if visited_pages is None:
        visited_pages = set()

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href.endswith('.pdf'):
            pdf_links.append(urljoin(url, href))

    visited_pages.add(url)

    for link in soup.find_all('a'):
        href = link.get('href')
        absolute_url = urljoin(url, href)
        if absolute_url not in visited_pages and absolute_url.startswith(url):
            pdf_links += scrape_pdf_links(absolute_url, visited_pages)

    return pdf_links

def download_pdf(url, folder):
    response = requests.get(url)
    file_name = os.path.basename(url)
    file_path = os.path.join(folder, file_name)

    with open(file_path, 'wb') as file:
        file.write(response.content)

    print(f"Downloaded: {file_name}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='PDF Scraper')
parser.add_argument('--url', '-u', default='', type=str, help='Website URL to scrape PDF links from')
parser.add_argument('--output-dir', '-o', default='', type=str, help='Folder path to save downloaded PDF files')
args = parser.parse_args()

# Convert relative paths to absolute paths
output_dir = os.path.abspath(args.output_dir)

# Scrape PDF links
pdf_links = scrape_pdf_links(args.url)

# Download PDF files
for link in pdf_links:
    download_pdf(link, output_dir)